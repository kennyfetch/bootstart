"""Check the license of every installed Python distribution against the project's allow-list.

GitHub's dependency graph does not read uv.lock, so it misses transitive Python dependencies. This
script checks the installed environment instead, using the same allow-list as the dependency-review
workflow: `.github/dependency-review-config.yml`.

Each distribution ends up allowed, not allowed, malformed (an expression that is not valid SPDX) or
undetermined. Not allowed and malformed fail the check. Undetermined is reported without failing,
as in dependency-review: review it by hand and record the outcome in docs/THIRD_PARTY.md.
"""

import re
import sys
import tomllib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path
from typing import cast

import yaml

CONFIG_RELATIVE_PATH = Path(".github") / "dependency-review-config.yml"
EXIT_FAILED = 1
EXIT_BAD_CONFIG = 2

SPDX_TOKEN = re.compile(r"\(|\)|[^\s()]+")
OPERATORS = frozenset({"AND", "OR", "WITH"})
PARENTHESES = frozenset({"(", ")"})
# SPDX families never in the default allow-list: copyleft, non-commercial, source-available.
RESTRICTIVE_SPDX_ID = re.compile(
    r"^(A?L?GPL|MPL-1|EPL|EUPL|CDDL|CPL|OSL|SSPL|BUSL|Elastic|PolyForm|CC-BY-(NC|ND|SA))",
    re.IGNORECASE,
)
# License classifiers that look restrictive even when they are not in SPDX_BY_CLASSIFIER.
RESTRICTIVE_CLASSIFIER = re.compile(r"GPL|SSPL|BUSL|Commons Clause|Non-?Commercial", re.IGNORECASE)

# Trove classifiers mapped to SPDX identifiers; copyleft ones are listed so they are caught.
SPDX_BY_CLASSIFIER = {
    "License :: OSI Approved :: MIT License": "MIT",
    "License :: OSI Approved :: MIT No Attribution License (MIT-0)": "MIT-0",
    "License :: OSI Approved :: Apache Software License": "Apache-2.0",
    "License :: OSI Approved :: BSD License": "BSD-3-Clause",
    "License :: OSI Approved :: ISC License (ISCL)": "ISC",
    "License :: OSI Approved :: Python Software Foundation License": "PSF-2.0",
    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)": "MPL-2.0",
    "License :: OSI Approved :: zlib/libpng License": "Zlib",
    "License :: OSI Approved :: The Unlicense (Unlicense)": "Unlicense",
    "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication": "CC0-1.0",
    "License :: OSI Approved :: GNU General Public License (GPL)": "GPL-3.0-or-later",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)": "GPL-2.0-only",
    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)": (
        "GPL-2.0-or-later"
    ),
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)": "GPL-3.0-only",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)": (
        "GPL-3.0-or-later"
    ),
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)": (
        "LGPL-2.0-or-later"
    ),
    "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)": "LGPL-2.0-only",
    "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)": (
        "LGPL-2.0-or-later"
    ),
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)": "LGPL-3.0-only",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)": (
        "LGPL-3.0-or-later"
    ),
    "License :: OSI Approved :: GNU Affero General Public License v3": "AGPL-3.0-only",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)": (
        "AGPL-3.0-or-later"
    ),
    "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)": "EPL-2.0",
    "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)": "EUPL-1.2",
}


class LicenseExpressionError(ValueError):
    """A license expression that does not follow the SPDX syntax."""


@dataclass(frozen=True)
class Policy:
    """Allowed SPDX identifiers and excepted packages, all lowercase."""

    allowed_licenses: frozenset[str]
    excepted_packages: frozenset[str]


@dataclass(frozen=True)
class PackageLicense:
    """The license metadata of one installed distribution."""

    name: str
    expression: str | None
    classifiers: tuple[str, ...]
    declared: str | None


@dataclass
class Report:
    """Packages that fail the check (not allowed, malformed) or need a manual review (unknown)."""

    not_allowed: list[str] = field(default_factory=list[str])
    malformed: list[str] = field(default_factory=list[str])
    unknown: list[str] = field(default_factory=list[str])

    @property
    def has_failures(self) -> bool:
        return bool(self.not_allowed or self.malformed)


def normalize_name(name: str) -> str:
    """Package name in its PEP 503 normalized form: `Typing_Extensions` → `typing-extensions`."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_policy(text: str) -> Policy:
    """Read the allow-list and the per-package exceptions from the dependency-review config.

    Raises:
        ValueError: If the configuration is not a mapping or a list holds non-string items.
    """
    loaded: object = yaml.safe_load(text)
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError("the configuration is not a YAML mapping")
    config = cast("dict[str, object]", loaded)
    exceptions = _string_list(config, "allow-dependencies-licenses")
    return Policy(
        allowed_licenses=frozenset(item.lower() for item in _string_list(config, "allow-licenses")),
        excepted_packages=frozenset(
            normalize_name(purl.removeprefix("pkg:pypi/").split("@")[0])
            for purl in exceptions
            if purl.startswith("pkg:pypi/")
        ),
    )


def _string_list(config: dict[str, object], key: str) -> list[str]:
    value = config.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"'{key}' must be a list")
    items = cast("list[object]", value)
    if not all(isinstance(item, str) for item in items):
        raise ValueError(f"'{key}' must only contain strings")
    return cast("list[str]", items)


def is_expression_allowed(expression: str, allowed_licenses: frozenset[str]) -> bool:
    """Evaluate an SPDX expression: `A OR B` needs one allowed side, `A AND B` needs both.

    Raises:
        LicenseExpressionError: If the expression is not valid SPDX syntax.
    """
    return _ExpressionParser(SPDX_TOKEN.findall(expression), allowed_licenses).parse()


class _ExpressionParser:
    """Recursive-descent parser: or-expression := and-expression ("OR" and-expression)*."""

    def __init__(self, tokens: list[str], allowed_licenses: frozenset[str]) -> None:
        self.tokens = tokens
        self.allowed_licenses = allowed_licenses
        self.position = 0

    def parse(self) -> bool:
        if not self.tokens:
            raise LicenseExpressionError("empty expression")
        result = self._parse_or()
        if self.position < len(self.tokens):
            raise LicenseExpressionError(f"unexpected '{self.tokens[self.position]}'")
        return result

    def _peek(self) -> str | None:
        return self.tokens[self.position].upper() if self.position < len(self.tokens) else None

    def _next(self) -> str:
        if self.position >= len(self.tokens):
            raise LicenseExpressionError("expression ends too early")
        self.position += 1
        return self.tokens[self.position - 1]

    def _parse_or(self) -> bool:
        result = self._parse_and()
        while self._peek() == "OR":
            self.position += 1
            right = self._parse_and()  # always parsed, so syntax errors on the right still surface
            result = result or right
        return result

    def _parse_and(self) -> bool:
        result = self._parse_atom()
        while self._peek() == "AND":
            self.position += 1
            right = self._parse_atom()
            result = result and right
        return result

    def _parse_atom(self) -> bool:
        symbol = self._next()
        if symbol == "(":
            result = self._parse_or()
            if self._next() != ")":
                raise LicenseExpressionError("missing ')'")
            return result
        if symbol == ")" or symbol.upper() in OPERATORS:
            raise LicenseExpressionError(f"unexpected '{symbol}'")
        if self._peek() == "WITH":
            self.position += 1
            exception = self._next()
            if exception in PARENTHESES or exception.upper() in OPERATORS:
                raise LicenseExpressionError(f"unexpected '{exception}' after WITH")
        return symbol.rstrip("+").lower() in self.allowed_licenses


def license_of(package: PackageLicense, allowed_licenses: frozenset[str]) -> str | None:
    """Best SPDX expression for a package: License-Expression, classifiers, then License.

    The free-form License field is used only when every identifier in it is a recognized SPDX
    identifier (allowed, or from a restrictive family); text such as "BSD" stays undetermined.
    """
    if package.expression:
        return package.expression
    from_classifiers = sorted(
        {spdx for classifier in package.classifiers if (spdx := _classifier_license(classifier))}
    )
    if from_classifiers:
        # Several license classifiers mean "any of these" (dual licensing).
        return " OR ".join(from_classifiers)
    declared = (package.declared or "").strip()
    if declared and _is_recognized_spdx(declared, allowed_licenses):
        return declared
    return None


def _classifier_license(classifier: str) -> str | None:
    if classifier in SPDX_BY_CLASSIFIER:
        return SPDX_BY_CLASSIFIER[classifier]
    if classifier.startswith("License ::") and RESTRICTIVE_CLASSIFIER.search(classifier):
        name = classifier.rsplit("::", 1)[-1]
        return "LicenseRef-" + "-".join(re.findall(r"[A-Za-z0-9.]+", name))
    return None


def _is_recognized_spdx(text: str, allowed_licenses: frozenset[str]) -> bool:
    tokens = SPDX_TOKEN.findall(text)
    identifiers = [
        token
        for index, token in enumerate(tokens)
        if token not in PARENTHESES
        and token.upper() not in OPERATORS
        and (index == 0 or tokens[index - 1].upper() != "WITH")  # skip exception names
    ]
    return bool(identifiers) and all(
        identifier.rstrip("+").lower() in allowed_licenses or RESTRICTIVE_SPDX_ID.match(identifier)
        for identifier in identifiers
    )


def check_packages(packages: Iterable[PackageLicense], policy: Policy, project_name: str) -> Report:
    """Classify every package except the project itself and the excepted ones."""
    report = Report()
    skipped = {normalize_name(project_name), *policy.excepted_packages}
    for package in packages:
        if normalize_name(package.name) in skipped:
            continue
        expression = license_of(package, policy.allowed_licenses)
        if expression is None:
            report.unknown.append(package.name)
            continue
        try:
            if not is_expression_allowed(expression, policy.allowed_licenses):
                report.not_allowed.append(f"{package.name} ({expression})")
        except LicenseExpressionError as error:
            report.malformed.append(f"{package.name} ({expression}): {error}")
    return report


def installed_packages() -> Iterator[PackageLicense]:
    """License metadata of every distribution installed in the current environment."""
    for distribution in metadata.distributions():
        fields = distribution.metadata
        yield PackageLicense(
            name=str(fields["Name"]),
            expression=fields.get("License-Expression"),
            classifiers=tuple(str(item) for item in fields.get_all("Classifier") or []),
            declared=fields.get("License"),
        )


def find_config(start: Path) -> Path | None:
    """Return the allow-list file from `start` or its closest parent that has one."""
    for folder in (start, *start.parents):
        candidate = folder / CONFIG_RELATIVE_PATH
        if candidate.is_file():
            return candidate
    return None


def print_report(report: Report, config: Path) -> None:
    for name in sorted(set(report.unknown), key=str.lower):
        print(f"License unknown, review it by hand: {name}")
    for entry in sorted(set(report.malformed), key=str.lower):
        print(f"License expression malformed: {entry}")
    for entry in sorted(set(report.not_allowed), key=str.lower):
        print(f"License not allowed: {entry}")
    if report.has_failures:
        print(f"Allowed licenses and exceptions: {config}")
    else:
        print("All package licenses are allowed.")


def main() -> int:
    config = find_config(Path.cwd())
    if config is None:
        print(f"License check: {CONFIG_RELATIVE_PATH} not found in this folder or its parents.")
        return EXIT_BAD_CONFIG
    try:
        policy = parse_policy(config.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError) as error:
        print(f"License check: cannot read {config}: {error}")
        return EXIT_BAD_CONFIG
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    report = check_packages(installed_packages(), policy, project_name=pyproject["project"]["name"])
    print_report(report, config)
    return EXIT_FAILED if report.has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
