from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)

from infrastructure.database.connection import DatabaseManager
from repositories.product_repository import ProductRepository
from application.services.product_service import ProductCreationService


def test_product_creation_service_round_trip():

    database_manager = DatabaseManager()
    product_repository = ProductRepository()

    product_service = ProductCreationService(
        product_repository=product_repository,
        database_manager=database_manager,
    )

    product = product_service.create(
        canonical_name="EcoCash",
        aliases={
            "Eco Cash",
            "EcoCash Mobile Money",
        },
    )

    retrieved = product_service.get_by_id(
        product.reference,
    )

    assert retrieved is not None

    assert retrieved.reference == product.reference
    assert retrieved.kind == IdentityKind.PRODUCT
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    assert (
        retrieved.representations.canonical_name
        == "EcoCash"
    )

    assert retrieved.representations.aliases == {
        "Eco Cash",
        "EcoCash Mobile Money",
    }
    print("Test Passed")

test_product_creation_service_round_trip()