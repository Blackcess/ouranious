from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)
from uuid import uuid4


def test_product_creation_service_round_trip(service_environment):
    product_service = service_environment["product"]
    canonical_name = f"EcoCash {uuid4().hex}"
    aliases = {f"Eco Cash {uuid4().hex}", f"EcoCash Mobile Money {uuid4().hex}"}

    result = product_service.create(canonical_name=canonical_name, aliases=aliases)
    product = result.entity
    service_environment["track_identity"](product)
    assert result.action.value == "created"

    retrieved = product_service.get_by_id(
        product.reference,
    )

    assert retrieved is not None

    assert retrieved.reference == product.reference
    assert retrieved.kind == IdentityKind.PRODUCT
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    assert (
        retrieved.representations.canonical_name
        == canonical_name
    )

    assert retrieved.representations.aliases == aliases
