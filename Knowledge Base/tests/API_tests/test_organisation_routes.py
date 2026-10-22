from types import SimpleNamespace
from uuid import uuid4
import pytest

from fastapi.testclient import TestClient

from API.app import app
from API.v1.dependancies.organisation_dependancies import get_organisation_service
from domain_models.Identity_model.Organisation_model.organisation_classification import (
    OrganisationClassification,
)
from domain_models.Identity_model.Organisation_model.classification_specific_domain_model.startup.start_up import (
    StartupBusinessModels,
    StartupStages,
)


class FakeOrganisationCreationService:
    def __init__(self):
        self.calls = []

    def create_startup(
        self,
        *,
        canonical_name,
        founding_year,
        stage,
        business_model,
        aliases=None,
    ):
        self.calls.append({
            "canonical_name": canonical_name,
            "founding_year": founding_year,
            "stage": stage,
            "business_model": business_model,
            "aliases": aliases,
        })

        startup = SimpleNamespace(
            founding_year=founding_year,
            stage=stage,
            business_model=business_model,
        )

        organisation = SimpleNamespace(
            reference=SimpleNamespace(value=uuid4()),
            representations=SimpleNamespace(
                canonical_name=canonical_name,
                aliases=aliases or set(),
            ),
            get_classification_model=lambda classification: (
                startup
                if classification == OrganisationClassification.STARTUP
                else None
            ),
        )

        return organisation


fake_service = FakeOrganisationCreationService()

@pytest.fixture
def setup_client():
    fake_service = FakeOrganisationCreationService()

    def override_service():
        return fake_service

    app.dependency_overrides[
        get_organisation_service
    ] = override_service

    with TestClient(app) as client:
        yield client, fake_service

    app.dependency_overrides.pop(
        get_organisation_service,
        None,
    )

# test 1 : Successful creation

def test_create_startup_returns_201(setup_client):
    client, fake_service = setup_client

    response = client.post(
        "/api/v1/organisations/startups",
        json={
            "canonical_name": "Example Startup",
            "founding_year": 2024,
            "stage": "pre_seed",
            "business_model": "b2b",
            "aliases": ["Example"],
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["canonical_name"] == "Example Startup"
    assert body["founding_year"] == 2024
    assert body["stage"] == "pre_seed"
    assert body["business_model"] == "b2b"
    assert body["aliases"] == ["Example"]
    assert "id" in body

    assert len(fake_service.calls) == 1
    assert fake_service.calls[0]["aliases"] == {"Example"}


# Test 2: Invalid Enum rejected before service invocation
def test_invalid_stage_returns_422(setup_client):
    client, fake_service = setup_client

    response = client.post(
        "/api/v1/organisations/startups",
        json={
            "canonical_name": "Example Startup",
            "founding_year": 2024,
            "stage": "invalid_stage",
            "business_model": "b2b",
        },
    )

    assert response.status_code == 422
    assert fake_service.calls == []

# Test 3: Unexpected Field Rejected

def test_unknown_field_returns_422(setup_client):
    client, fake_service = setup_client

    response = client.post(
        "/api/v1/organisations/startups",
        json={
            "canonical_name": "Example Startup",
            "founding_year": 2024,
            "stage": "pre_seed",
            "business_model": "b2b",
            "unexpected_field": "value",
        },
    )

    assert response.status_code == 422
    assert fake_service.calls == []