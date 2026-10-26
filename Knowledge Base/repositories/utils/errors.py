class RepositoryIntegrityError(Exception):
    """Raised when persisted data violates domain integrity."""


class RepositoryConflictError(Exception):
    """Raised when a create operation conflicts with an existing key."""


class RepositoryReferenceError(Exception):
    """Raised when a persisted reference points to a missing record."""


class RepositoryNotFoundError(Exception):
    """Raised when an operation requires a record that does not exist."""


def translate_integrity_error(operation: str, error: Exception) -> Exception:
    """Translate common MySQL integrity failures without hiding other errors."""
    from pymysql.err import IntegrityError

    if not isinstance(error, IntegrityError):
        return error
    code = error.args[0] if error.args else None
    if code == 1062:
        return RepositoryConflictError(f"{operation} conflicts with an existing identifier.")
    if code in (1451, 1452):
        return RepositoryReferenceError(f"{operation} references a missing or protected record.")
    return RepositoryIntegrityError(f"{operation} violates a database integrity constraint.")
