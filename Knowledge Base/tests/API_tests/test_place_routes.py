from uuid import uuid4
from unittest.mock import Mock

from fastapi.testclient import TestClient
from application.resolution.create_result import CreateAction, CreateResult
from application.resolution.identity.contracts import (
    IdentityResolutionResult,
    ResolutionOutcome,
)

from API.app import app
from API.v1.dependancies.place_dependancies import get_place_service


def test_create_place():
    place_id = uuid4()
    service = Mock()

    # Configure a realistic domain Place as the service return value.
    from domain_models.Identity_model.identity import IdentityRepresentations
    from domain_models.Identity_model.Place_model.place import Place, PlaceKind

    place = Place(
        representations=IdentityRepresentations(
            canonical_name="Harare",
            aliases={"Salisbury"},
        ),
        place_kind=PlaceKind.CITY,
    )
    # Give the test object a deterministic reference.
    from domain_models.Identity_model.identity import IdentityReference
    place._reference = IdentityReference(value=place_id)

    resolution = IdentityResolutionResult(outcome=ResolutionOutcome.NO_MATCH)
    service.create.return_value = CreateResult(
        outcome=ResolutionOutcome.NO_MATCH,
        action=CreateAction.CREATED,
        entity=place,
        resolution=resolution,
    )

    app.dependency_overrides[get_place_service] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/places",
                json={
                    "canonical_name": "Harare",
                    "place_kind": "city",
                    "aliases": ["Salisbury"],
                },
            )

        assert response.status_code == 201
        assert response.json()["outcome"] == "no_match"
        assert response.json()["action"] == "created"
        assert response.json()["entity"]["id"] == str(place_id)
        assert response.json()["entity"]["canonical_name"] == "Harare"
        assert response.json()["entity"]["aliases"] == ["Salisbury"]
        assert response.json()["entity"]["kind"] == "city"

        service.create.assert_called_once_with(
            canonical_name="Harare",
            place_kind=PlaceKind.CITY,
            aliases={"Salisbury"},
        allow_possible_duplicate=False,
        )
    finally:
        app.dependency_overrides.clear()


def test_get_place_not_found():
    service = Mock()
    service.get_by_id.return_value = None

    app.dependency_overrides[get_place_service] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/places/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Place not found"
    finally:
        app.dependency_overrides.clear()
