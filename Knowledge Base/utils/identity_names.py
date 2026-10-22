"""Name normalization shared by application logic and repository searches."""

import re


_WHITESPACE = re.compile(r"\s+")


def normalize_identity_name(value: str) -> str:
    """Trim, collapse whitespace, and casefold without removing punctuation/accents."""

    if not isinstance(value, str):
        raise TypeError("identity name must be a string")
    return _WHITESPACE.sub(" ", value.strip()).casefold()
