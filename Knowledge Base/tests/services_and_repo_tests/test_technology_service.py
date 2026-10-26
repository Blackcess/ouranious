from domain_models.Identity_model.identity import (
    IdentityKind,
    LifecycleState,
)
from uuid import uuid4


def test_technology_creation_service_round_trip(service_environment):
    technology_service = service_environment["technology"]
    canonical_name = f"React {uuid4().hex}"
    aliases = {f"React.js {uuid4().hex}", f"ReactJS {uuid4().hex}"}

    result = technology_service.create(canonical_name=canonical_name, aliases=aliases)
    technology = result.entity
    service_environment["track_identity"](technology)
    assert result.action.value == "created"

    retrieved = technology_service.get_by_id(
        technology.reference,
    )

    assert retrieved is not None

    assert retrieved.reference == technology.reference
    assert retrieved.kind == IdentityKind.TECHNOLOGY
    assert retrieved.lifecycle_state == LifecycleState.CANONICAL

    assert (
        retrieved.representations.canonical_name
        == canonical_name
    )

    assert retrieved.representations.aliases == aliases
