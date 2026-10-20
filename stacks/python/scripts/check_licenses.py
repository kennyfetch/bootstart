"""Check the license of every installed Python distribution against the project's allow-list.

GitHub's dependency graph does not read uv.lock, so it misses transitive Python dependencies. This
script checks the installed environment instead, using the same allow-list as the dependency-review
workflow: `.github/dependency-review-config.yml`.

A disallowed license fails the check. A license that cannot be determined is reported but does not
fail, as in dependency-review: review it by hand and record the outcome in docs/THIRD_PARTY.md.
"""

import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

CONFIG_RELATIVE_PATH = Path(".github") / "dependency-review-config.yml"
EXIT_DISALLOWED = 1
EXIT_NO_CONFIG = 2
SPDX_EXPRESSION = re.compile(r"[A-Za-z0-9.+\-]+( (AND|OR|WITH) [A-Za-z0-9.+\-]+)*")
# Free-form License fields are trusted only when clearly allowed or clearly restrictive.
RESTRICTIVE_HINT = re.compile(r"GPL|SSPL|BUSL|Commons-Clause|-NC\b", re.IGNORECASE)

# Trove classifiers mapped to SPDX identifiers. Copyleft ones are listed so that they are caught,
# not merely reported as unknown.
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


def find_config(start: Path) -> Path | None:
    """Return the allow-list file from `start` or its closest parent that has one."""
    for folder in (start, *start.parents):
        candidate = folder / CONFIG_RELATIVE_PATH
        if candidate.is_file():
            return candidate
    return None


def read_yaml_list(text: str, key: str) -> list[str]:
    """Read a top-level list (`key:` then `  - item` lines) from simple YAML, without a parser."""
    items: list[str] = []
    in_list = False
    for line in text.splitlines():
        if re.match(rf"^{re.escape(key)}:", line):
            in_list = True
            continue
        if in_list:
            item = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if item:
                items.append(item.group(1).strip("'\""))
            elif line.strip() and not line.lstrip().startswith("#"):
                break
    return items


def is_expression_allowed(expression: str, allowed: set[str]) -> bool:
    """Evaluate an SPDX expression: OR needs one allowed side, AND needs both."""
    tokens = re.findall(r"\(|\)|[^\s()]+", expression)
    position = 0

    def parse_or() -> bool:
        nonlocal position
        result = parse_and()
        while position < len(tokens) and tokens[position].upper() == "OR":
            position += 1
            result = parse_and() or result
        return result

    def parse_and() -> bool:
        nonlocal position
        result = parse_atom()
        while position < len(tokens) and tokens[position].upper() == "AND":
            position += 1
            result = parse_atom() and result
        return result

    def parse_atom() -> bool:
        nonlocal position
        symbol = tokens[position]
        position += 1
        if symbol == "(":
            result = parse_or()
            position += 1  # closing parenthesis
            return result
        if position < len(tokens) and tokens[position].upper() == "WITH":
            position += 2  # an exception only relaxes the license it applies to
        return symbol.rstrip("+").lower() in allowed

    return parse_or()


def restrictive_reference(classifier: str) -> str:
    """Turn an unmapped copyleft-looking classifier into a LicenseRef that is never allowed."""
    name = classifier.rsplit("::", 1)[-1]
    return "LicenseRef-" + "-".join(re.findall(r"[A-Za-z0-9.]+", name))


def license_of(distribution: metadata.Distribution, allowed: set[str]) -> str | None:
    """Best SPDX expression for a distribution: License-Expression, classifiers, then License."""
    fields = distribution.metadata
    if expression := fields.get("License-Expression"):
        return expression
    license_classifiers = [
        classifier
        for classifier in fields.get_all("Classifier") or []
        if classifier.startswith("License ::")
    ]
    from_classifiers = [
        SPDX_BY_CLASSIFIER.get(classifier) or restrictive_reference(classifier)
        for classifier in license_classifiers
        if classifier in SPDX_BY_CLASSIFIER or RESTRICTIVE_HINT.search(classifier)
    ]
    if from_classifiers:
        # Several license classifiers mean "any of these" (dual licensing).
        return " OR ".join(sorted(set(from_classifiers)))
    declared = (fields.get("License") or "").strip()
    if SPDX_EXPRESSION.fullmatch(declared) and (
        is_expression_allowed(declared, allowed) or RESTRICTIVE_HINT.search(declared)
    ):
        return declared
    return None


def main() -> int:
    config = find_config(Path.cwd())
    if config is None:
        print(f"License check: {CONFIG_RELATIVE_PATH} not found in this folder or its parents.")
        return EXIT_NO_CONFIG
    config_text = config.read_text(encoding="utf-8")
    allowed = {license_id.lower() for license_id in read_yaml_list(config_text, "allow-licenses")}
    excepted = {
        purl.removeprefix("pkg:pypi/").lower()
        for purl in read_yaml_list(config_text, "allow-dependencies-licenses")
        if purl.startswith("pkg:pypi/")
    }
    project_name = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"][
        "name"
    ]

    disallowed: list[str] = []
    unknown: list[str] = []
    for distribution in metadata.distributions():
        name = distribution.metadata["Name"]
        normalized_name = re.sub(r"[-_.]+", "-", name).lower()
        if normalized_name in {project_name.lower(), *excepted}:
            continue
        expression = license_of(distribution, allowed)
        if expression is None:
            unknown.append(name)
        elif not is_expression_allowed(expression, allowed):
            disallowed.append(f"{name} ({expression})")

    for name in sorted(set(unknown), key=str.lower):
        print(f"License unknown, review it by hand: {name}")
    for entry in sorted(set(disallowed), key=str.lower):
        print(f"License not allowed: {entry}")
    if disallowed:
        print(f"Allowed licenses and exceptions: {config}")
        return EXIT_DISALLOWED
    print("All package licenses are allowed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
