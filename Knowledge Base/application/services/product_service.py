from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Product_model.product import Product

from repositories.product_repository import ProductRepository
from infrastructure.database.connection import DatabaseManager
from application.services.create_orchestration import resolve_and_create_identity
from application.services.identity_resolution_service import IdentityResolutionService
from application.resolution.create_result import CreateResult
from application.resolution.identity.contracts import IdentityResolutionResult


class ProductService:

    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        database_manager: DatabaseManager,
        identity_resolution_service: IdentityResolutionService,
    ):
        self._product_repository = product_repository
        self._database_manager = database_manager
        self._identity_resolution_service = identity_resolution_service

    def create(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
        allow_possible_duplicate: bool = False,
    ) -> CreateResult[Product, IdentityResolutionResult]:
        """
        Create and persist a Product.

        Returns the persisted Product including its generated
        IdentityReference.
        """

        product = Product(
            representations=IdentityRepresentations(
                canonical_name=canonical_name,
                aliases=set(aliases or ()),
            ),
            lifecycle_state=lifecycle_state,
        )

        return resolve_and_create_identity(
            product,
            repository=self._product_repository,
            database_manager=self._database_manager,
            resolver=self._identity_resolution_service,
            allow_possible_duplicate=allow_possible_duplicate,
        )

    def get_by_id(
        self,
        reference: IdentityReference | UUID,
    ) -> Product | None:
        """
        Retrieve a Product by identity reference.
        """

        with self._database_manager.connection() as connection:
            return self._product_repository.get_by_id(
                reference,
                connection=connection,
            )
