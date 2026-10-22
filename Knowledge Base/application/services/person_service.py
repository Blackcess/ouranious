from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Person_model.person import Person

from repositories.person_repository import PersonRepository
from infrastructure.database.connection import DatabaseManager


class PersonService:

    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        database_manager: DatabaseManager,
    ):
        self._person_repository = person_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ) -> Person:
        """
        Create and persist a Person.

        Returns the persisted Person including its generated
        IdentityReference.
        """

        person = Person(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            lifecycle_state=lifecycle_state,
        )

        return self._persist_person(person)

    def _persist_person(
        self,
        person: Person,
    ) -> Person:
        """
        Persist a Person atomically.
        """

        with self._database_manager.transaction() as connection:
            self._person_repository.save(
                person,
                connection=connection,
            )

        return person

    def get_by_id(
        self,
        reference: IdentityReference | UUID,
    ) -> Person | None:
        """
        Retrieve a Person by identity reference.
        """

        with self._database_manager.connection() as connection:
            return self._person_repository.get_by_id(
                reference,
                connection=connection,
            )