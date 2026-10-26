from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)
from uuid import uuid4


def test_industry_creation_service_round_trip(service_environment):
    industry_service = service_environment["industry"]
    canonical_name = f"Financial Technology {uuid4().hex}"
    aliases = {f"Fintech {uuid4().hex}", f"Financial Tech {uuid4().hex}"}

    result = industry_service.create(canonical_name=canonical_name, aliases=aliases)
    industry = result.entity
    service_environment["track_identity"](industry)
    assert result.action.value == "created"

    retrieved = industry_service.get_by_id(
        industry.reference,
    )

    assert retrieved is not None

    # Identity reference.
    assert retrieved.reference == industry.reference

    # Identity kind.
    assert retrieved.kind == IdentityKind.INDUSTRY

    # Lifecycle state.
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    # Canonical name.
    assert (
        retrieved.representations.canonical_name
        == canonical_name
    )

    # Aliases.
    assert retrieved.representations.aliases == aliases

