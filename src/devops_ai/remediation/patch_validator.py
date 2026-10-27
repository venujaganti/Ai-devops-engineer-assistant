
from pathlib import PurePosixPath


MAX_PATCH_CHARS = 8000


def validate_proposed_patch(patch: object) -> tuple[bool, str]:
    if patch is None:
        return True, "No patch was proposed."

    if not isinstance(patch, str):
        return False, "Patch must be text."

    if not patch.strip():
        return False, "Patch is empty."

    if len(patch) > MAX_PATCH_CHARS:
        return False, "Patch exceeds the size limit."

    lines = patch.splitlines()
    if len(lines) < 3:
        return False, "Patch does not look like a unified diff."

    file_headers = [
        line for line in lines
        if line.startswith("--- ") or line.startswith("+++ ")
    ]
    if not file_headers:
        return False, "No unified-diff file headers were found."

    for line in file_headers:
        raw_path = line[4:].strip().split("\t", 1)[0]
        if raw_path == "/dev/null":
            continue

        # Git diff prefixes a/ and b/ are accepted.
        candidate = raw_path[2:] if raw_path.startswith(("a/", "b/")) else raw_path
        path = PurePosixPath(candidate)

        if path.is_absolute() or ".." in path.parts:
            return False, "Patch contains a path outside the repository."

        if candidate.startswith("~"):
            return False, "Home-directory paths are not allowed."

    if any("\x00" in line for line in lines):
        return False, "Patch contains a null byte."

    return True, "Patch passed basic display-safety checks."
