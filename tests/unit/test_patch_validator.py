
from src.devops_ai.remediation.patch_validator import validate_proposed_patch


def test_none_patch_is_allowed():
    valid, _ = validate_proposed_patch(None)
    assert valid is True


def test_basic_unified_diff_is_allowed():
    patch = (
        "--- a/deployment.yaml\n"
        "+++ b/deployment.yaml\n"
        "@@ -1,1 +1,1 @@\n"
        "-replicas: 1\n"
        "+replicas: 2\n"
    )

    valid, _ = validate_proposed_patch(patch)
    assert valid is True


def test_parent_directory_path_is_rejected():
    patch = (
        "--- a/../secrets.txt\n"
        "+++ b/../secrets.txt\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
    )

    valid, _ = validate_proposed_patch(patch)
    assert valid is False


def test_non_text_patch_is_rejected():
    valid, _ = validate_proposed_patch(123)
    assert valid is False
