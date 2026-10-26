"""Manually callable examples of the Person service create-result contract.

These are ordinary Python functions, not pytest tests. They use the configured
development database and create uniquely named example records. The seed
records used by the exact-match and possible-duplicate examples remain in the
database so the returned result can be inspected after the function returns.

Example from the project root::

    from tests.services_and_repo_tests.person_creation_result_examples import (
        show_no_match, show_exact_match, show_possible_duplicate,
    )

    result = show_possible_duplicate()
    print(result)
    print(result.action, result.outcome, result.entity, result.resolution.matches)
"""

from uuid import uuid4

from API.v1.dependancies.identity_resolution_dependancies import (
    get_identity_resolution_service,
)
from application.services.person_service import PersonService
from infrastructure.database.connection import DatabaseManager
from repositories.person_repository import PersonRepository


def _person_service() -> PersonService:
    """Build the same service dependencies used by the application layer."""
    return PersonService(
        person_repository=PersonRepository(),
        database_manager=DatabaseManager(),
        identity_resolution_service=get_identity_resolution_service(),
    )


def show_no_match():
    """Create a unique Person and return its CREATED / NON_MATCH result."""
    service = _person_service()
    marker = uuid4().hex
    name = f"Resolution Example Person {marker}"
    return service.create(canonical_name= name)


def show_exact_match():
    """Create a Person, repeat its canonical name, and return the exact result."""
    service = _person_service()
    # canonical_name = f"Resolution Example Exact Person {uuid4().hex}"
    canonical_name = "Strive Masiyiwa"
    service.create(canonical_name=canonical_name)
    return service.create(canonical_name=canonical_name)


def show_possible_duplicate():
    """Seed one Person and return the blocked alias-overlap result."""
    service = _person_service()
    shared_alias = f"Resolution Example Shared Alias {uuid4().hex}"
    service.create(
        canonical_name=f"Resolution Example Alias Person A {uuid4().hex}",
        aliases={shared_alias},
    )
    return service.create(
        canonical_name=f"Resolution Example Alias Person B {uuid4().hex}",
        aliases={shared_alias},
    )


test_result = show_exact_match()

for match in test_result.resolution.matches:
    print(match.kind,"   ",match.identity.representations.canonical_name,f"\n")