import pytest
from check_licenses import (
    LicenseExpressionError,
    PackageLicense,
    Policy,
    check_packages,
    is_expression_allowed,
    license_of,
    parse_policy,
)

ALLOWED = frozenset({"mit", "apache-2.0", "bsd-3-clause"})


def make_package(
    name: str = "some-package",
    *,
    expression: str | None = None,
    classifiers: tuple[str, ...] = (),
    declared: str | None = None,
) -> PackageLicense:
    return PackageLicense(name, expression, classifiers, declared)


# --- parse_policy -------------------------------------------------------------------------------


def test_parse_policy_ignores_inline_comments() -> None:
    text = "allow-licenses:\n  - MIT # permissive\n  - Apache-2.0\n"

    policy = parse_policy(text)

    assert policy.allowed_licenses == frozenset({"mit", "apache-2.0"})


def test_parse_policy_reads_flow_lists() -> None:
    policy = parse_policy("allow-licenses: [MIT, 'BSD-3-Clause']\n")

    assert policy.allowed_licenses == frozenset({"mit", "bsd-3-clause"})


def test_parse_policy_keeps_pypi_exceptions_with_comments_and_versions() -> None:
    text = (
        "allow-licenses: [MIT]\n"
        "allow-dependencies-licenses:\n"
        "  - pkg:pypi/Some_Package  # ADR 0007\n"
        "  - pkg:pypi/other@1.2.3\n"
        "  - pkg:npm/left-pad\n"
    )

    policy = parse_policy(text)

    assert policy.excepted_packages == frozenset({"some-package", "other"})


def test_parse_policy_treats_missing_or_empty_lists_as_empty() -> None:
    policy = parse_policy("allow-dependencies-licenses: []\n")

    assert policy == Policy(allowed_licenses=frozenset(), excepted_packages=frozenset())


@pytest.mark.parametrize(
    "text",
    ["- just a list\n", "allow-licenses: MIT\n", "allow-licenses: [MIT, 42]\n"],
)
def test_parse_policy_rejects_invalid_structures(text: str) -> None:
    with pytest.raises(ValueError, match=r"allow-licenses|mapping"):
        parse_policy(text)


# --- is_expression_allowed ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("MIT", True),
        ("mit", True),
        ("GPL-3.0-only", False),
        ("MIT OR GPL-3.0-only", True),
        ("GPL-3.0-only OR MIT", True),
        ("MIT AND GPL-3.0-only", False),
        ("MIT AND Apache-2.0", True),
        ("(MIT OR GPL-3.0-only) AND Apache-2.0", True),
        ("MIT AND (GPL-3.0-only OR Elastic-2.0)", False),
        ("Apache-2.0 WITH LLVM-exception", True),
        ("GPL-2.0-only WITH Classpath-exception-2.0", False),
        ("Apache-2.0+", True),
    ],
)
def test_is_expression_allowed_evaluates_spdx_operators(expression: str, expected: bool) -> None:
    result = is_expression_allowed(expression, ALLOWED)

    assert result is expected


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "MIT)",
        "MIT) AND GPL-3.0-only",
        "(MIT",
        "MIT OR",
        "OR MIT",
        "MIT AND",
        "MIT MIT",
        "MIT WITH",
        "MIT WITH OR",
        "()",
    ],
)
def test_is_expression_allowed_rejects_malformed_expressions(expression: str) -> None:
    with pytest.raises(LicenseExpressionError):
        is_expression_allowed(expression, ALLOWED)


# --- license_of ---------------------------------------------------------------------------------


def test_license_of_prefers_license_expression() -> None:
    package = make_package(
        expression="Apache-2.0",
        classifiers=("License :: OSI Approved :: MIT License",),
        declared="BSD",
    )

    assert license_of(package, ALLOWED) == "Apache-2.0"


def test_license_of_joins_several_classifiers_with_or() -> None:
    package = make_package(
        classifiers=(
            "License :: OSI Approved :: MIT License",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3",
        )
    )

    assert license_of(package, ALLOWED) == "Apache-2.0 OR MIT"


def test_license_of_turns_unmapped_copyleft_classifier_into_a_license_ref() -> None:
    package = make_package(classifiers=("License :: OSI Approved :: GNU Free Documentation (GPL)",))

    result = license_of(package, ALLOWED)

    assert result is not None
    assert result.startswith("LicenseRef-")
    assert not is_expression_allowed(result, ALLOWED)


@pytest.mark.parametrize(
    "declared",
    [
        "MIT",
        "Elastic-2.0",
        "EPL-2.0",
        "MIT OR GPL-3.0-only",
        "GPL-2.0-only WITH Classpath-exception-2.0",
    ],
)
def test_license_of_uses_recognized_spdx_in_the_license_field(declared: str) -> None:
    package = make_package(declared=declared)

    assert license_of(package, ALLOWED) == declared


@pytest.mark.parametrize(
    "declared", [None, "", "BSD", "Apache 2.0", "See LICENSE file", "MIT or similar"]
)
def test_license_of_leaves_free_text_undetermined(declared: str | None) -> None:
    package = make_package(declared=declared)

    assert license_of(package, ALLOWED) is None


# --- check_packages -----------------------------------------------------------------------------


def test_check_packages_classifies_each_package() -> None:
    policy = Policy(allowed_licenses=ALLOWED, excepted_packages=frozenset({"excepted-pkg"}))
    packages = [
        make_package("my-project", declared="Proprietary"),
        make_package("excepted_pkg", expression="GPL-3.0-only"),
        make_package("fine", expression="MIT"),
        make_package("restricted", declared="Elastic-2.0"),
        make_package("broken", expression="MIT) AND GPL-3.0-only"),
        make_package("mystery", declared="See LICENSE file"),
    ]

    report = check_packages(packages, policy, project_name="My_Project")

    assert report.not_allowed == ["restricted (Elastic-2.0)"]
    assert report.malformed == ["broken (MIT) AND GPL-3.0-only): unexpected ')'"]
    assert report.unknown == ["mystery"]
    assert report.has_failures


def test_check_packages_passes_with_only_unknown_licenses() -> None:
    policy = Policy(allowed_licenses=ALLOWED, excepted_packages=frozenset())

    report = check_packages([make_package("mystery")], policy, project_name="project")

    assert report.unknown == ["mystery"]
    assert not report.has_failures
