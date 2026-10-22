
from dataclasses import fields
from uuid import uuid4, UUID

import pytest
from fastapi.testclient import TestClient

from domain_models.Identity_model.identity import IdentityKind
from domain_models.relationship_models.relationship_types.relationship_types import (
    RelationshipType,
)
from domain_models.relationship_models.relationship_types.relationship_type_specification import (
    specification_registry,
)

from API.app import app


@pytest.fixture(scope="module")
def client():
    # Uses real application dependencies and the configured MySQL database.
    # Deliberately does not use app.dependency_overrides.
    with TestClient(app) as test_client:
        yield test_client


def unique_name(prefix: str) -> str:
    return f"Integration Test {prefix} {uuid4().hex}"


def create_identity(client: TestClient, kind: IdentityKind) -> UUID:
    """Create a real identity through its API and return its database UUID."""

    name = unique_name(kind.name)

    payloads = {
        "PERSON": {
            "canonical_name": name,
            "aliases": [f"{name} Alias"],
        },
        "PLACE": {
            "canonical_name": name,
            "place_kind": "city",
            "aliases": [],
        },
        "INDUSTRY": {
            "canonical_name": name,
            "aliases": [],
        },
        "TECHNOLOGY": {
            "canonical_name": name,
            "aliases": [],
        },
        "PRODUCT": {
            "canonical_name": name,
            "aliases": [],
        },
        "ORGANISATION": {
            "canonical_name": name,
            "founding_year": 2024,
            "stage": "pre_seed",
            "business_model": "b2b",
            "aliases": [],
        },
    }

    endpoints = {
        "PERSON": "/api/v1/persons",
        "PLACE": "/api/v1/places",
        "INDUSTRY": "/api/v1/industries",
        "TECHNOLOGY": "/api/v1/technologies",
        "PRODUCT": "/api/v1/products",
        "ORGANISATION": "/api/v1/organisations/startups",
    }

    kind_name = kind.name

    if kind_name not in payloads:
        raise AssertionError(
            f"No integration-test identity factory for {kind_name}. "
            "Add the appropriate real identity creation endpoint."
        )

    response = client.post(
        endpoints[kind_name],
        json=payloads[kind_name],
    )

    assert response.status_code == 201, (
        f"Could not create {kind_name}: "
        f"HTTP {response.status_code}: {response.text}"
    )

    identity_id = response.json()["id"]
    assert UUID(identity_id)

    return UUID(identity_id)


def normalise_allowed_kind(allowed_kind) -> IdentityKind:
    """
    Handle specifications that permit either one IdentityKind
    or a collection of permitted IdentityKind values.
    """
    if isinstance(allowed_kind, IdentityKind):
        return allowed_kind

    allowed_kinds = list(allowed_kind)

    assert allowed_kinds, "Relationship specification has no allowed identity kinds"

    return allowed_kinds[0]


def build_valid_properties_payload(relationship_type: RelationshipType):
    """
    Construct the smallest valid property payload for a relationship.

    Property dataclasses in this project use optional fields. An empty
    object lets the DTO converter instantiate the correct dataclass
    using its defaults.
    """
    specification = specification_registry.get(relationship_type)
    properties_type = specification.properties_type

    if properties_type is None:
        return None

    # Fail clearly if a future property dataclass introduces required fields.
    required_fields = [
        field.name
        for field in fields(properties_type)
        if field.default.__class__.__name__ == "_MISSING_TYPE"
        and field.default_factory.__class__.__name__ == "_MISSING_TYPE"
    ]

    assert not required_fields, (
        f"{properties_type.__name__} has required fields without defaults: "
        f"{required_fields}. Update the test payload factory."
    )

    return {}


@pytest.mark.parametrize(
    "relationship_type",
    list(RelationshipType),
    ids=lambda relationship_type: relationship_type.value,
)
def test_create_and_retrieve_every_relationship_type(
    client: TestClient,
    relationship_type: RelationshipType,
):
    """
    Integration test for every registered relationship type.

    The identities are persisted first. The relationship is then
    persisted using their actual UUIDs and retrieved through a
    separate HTTP request.
    """
    specification = specification_registry.get(relationship_type)

    source_kind = normalise_allowed_kind(specification.allowed_source)
    target_kind = normalise_allowed_kind(specification.allowed_target)

    source_id = create_identity(client, source_kind)
    target_id = create_identity(client, target_kind)

    properties = build_valid_properties_payload(relationship_type)

    request_payload = {
        "source_id": str(source_id),
        "target_id": str(target_id),
        "relationship_type": relationship_type.value,
        "properties": properties,
    }

    # Create and persist the relationship.
    create_response = client.post(
        "/api/v1/relationships",
        json=request_payload,
    )

    assert create_response.status_code == 201, (
        f"Failed to create {relationship_type.value}: "
        f"HTTP {create_response.status_code}: {create_response.text}"
    )

    created = create_response.json()

    assert UUID(created["id"])
    relationship_id = created["id"]

    assert created["source_id"] == str(source_id)
    assert created["target_id"] == str(target_id)
    assert created["relationship_type"] == relationship_type.value

    # Retrieve the relationship from the persistence layer through
    # another HTTP request, rather than trusting only the POST response.
    get_response = client.get(
        f"/api/v1/relationships/{relationship_id}",
    )

    assert get_response.status_code == 200

    retrieved = get_response.json()

    assert retrieved["id"] == relationship_id
    assert retrieved["source_id"] == str(source_id)
    assert retrieved["target_id"] == str(target_id)
    assert retrieved["relationship_type"] == relationship_type.value
    assert retrieved["properties"] == created["properties"]


def test_create_relationship_with_missing_source_returns_404(
    client: TestClient,
):
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(uuid4()),
            "target_id": str(target_id),
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 404


def test_create_relationship_with_missing_target_returns_404(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": str(uuid4()),
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 404


def test_get_nonexistent_relationship_returns_404(
    client: TestClient,
):
    response = client.get(f"/api/v1/relationships/{uuid4()}")

    assert response.status_code == 404


def test_invalid_relationship_uuid_returns_422(
    client: TestClient,
):
    response = client.get("/api/v1/relationships/not-a-uuid")

    assert response.status_code == 422


def test_invalid_source_uuid_returns_422(
    client: TestClient,
):
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": "not-a-uuid",
            "target_id": str(target_id),
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_invalid_target_uuid_returns_422(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": "not-a-uuid",
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_unknown_relationship_type_returns_422(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": str(target_id),
            "relationship_type": "unknown_relationship",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_relationship_with_extra_request_field_returns_422(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": str(target_id),
            "relationship_type": "born_in",
            "properties": None,
            "unexpected_field": "not allowed",
        },
    )

    assert response.status_code == 422


def test_relationship_with_unexpected_properties_returns_422(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": str(target_id),
            "relationship_type": "born_in",
            "properties": {
                "unexpected_property": "not allowed",
            },
        },
    )

    assert response.status_code == 422


def test_incompatible_identity_kinds_return_422(
    client: TestClient,
):
    """
    A person and a place are valid for BORN_IN, but not for FOUNDED,
    whose target must be an organisation.
    """
    person_id = create_identity(client, IdentityKind.PERSON)
    place_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(person_id),
            "target_id": str(place_id),
            "relationship_type": "founded",
            "properties": {},
        },
    )

    assert response.status_code == 422


def test_missing_required_relationship_properties_return_422(
    client: TestClient,
):
    """
    Relationships with a property dataclass require a properties object.
    This checks the route's deserialization boundary.
    """
    person_id = create_identity(client, IdentityKind.PERSON)
    place_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(person_id),
            "target_id": str(place_id),
            "relationship_type": "founded",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_relationship_requires_source_id(
    client: TestClient,
):
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "target_id": str(target_id),
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_relationship_requires_target_id(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "relationship_type": "born_in",
            "properties": None,
        },
    )

    assert response.status_code == 422


def test_relationship_requires_relationship_type(
    client: TestClient,
):
    source_id = create_identity(client, IdentityKind.PERSON)
    target_id = create_identity(client, IdentityKind.PLACE)

    response = client.post(
        "/api/v1/relationships",
        json={
            "source_id": str(source_id),
            "target_id": str(target_id),
            "properties": None,
        },
    )

    assert response.status_code == 422
