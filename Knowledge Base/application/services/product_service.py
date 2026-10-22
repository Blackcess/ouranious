from uuid import UUID

from domain_models.Identity_model.identity import (
    IdentityReference,
    IdentityRepresentations,
    LifecycleState,
)
from domain_models.Identity_model.Product_model.product import Product

from repositories.product_repository import ProductRepository
from infrastructure.database.connection import DatabaseManager


class ProductService:

    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        database_manager: DatabaseManager,
    ):
        self._product_repository = product_repository
        self._database_manager = database_manager

    def create(
        self,
        *,
        canonical_name: str,
        aliases: set[str] | None = None,
        lifecycle_state: LifecycleState = LifecycleState.CANONICAL,
    ) -> Product:
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

        return self._persist_product(product)

    def _persist_product(
        self,
        product: Product,
    ) -> Product:
        """
        Persist a Product atomically.
        """

        with self._database_manager.transaction() as connection:
            self._product_repository.save(
                product,
                connection=connection,
            )

        return product

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