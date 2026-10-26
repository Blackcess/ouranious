from types import SimpleNamespace
from uuid import uuid4
import pytest

from fastapi.testclient import TestClient

from API.app import app
from API.v1.dependancies.organisation_dependancies import get_organisation_service
from application.resolution.create_result import CreateAction, CreateResult
from application.resolution.identity.contracts import (
    IdentityResolutionResult,
    ResolutionOutcome,
)
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
        allow_possible_duplicate=False,
    ):
        self.calls.append({
            "canonical_name": canonical_name,
            "founding_year": founding_year,
            "stage": stage,
            "business_model": business_model,
            "aliases": aliases,
            "allow_possible_duplicate": allow_possible_duplicate,
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

        if self.next_outcome is ResolutionOutcome.POSSIBLE_DUPLICATE:
            resolution = IdentityResolutionResult(
                outcome=ResolutionOutcome.POSSIBLE_DUPLICATE,
                ambiguous=True,
                candidates_truncated=True,
            )
            if not allow_possible_duplicate:
                return CreateResult(
                    outcome=resolution.outcome,
                    action=CreateAction.BLOCKED,
                    entity=None,
                    resolution=resolution,
                )
            return CreateResult(
                outcome=resolution.outcome,
                action=CreateAction.CREATED,
                entity=organisation,
                resolution=resolution,
                override_applied=True,
            )

        resolution = IdentityResolutionResult(outcome=ResolutionOutcome.NO_MATCH)
        return CreateResult(
            outcome=resolution.outcome,
            action=CreateAction.CREATED,
            entity=organisation,
            resolution=resolution,
        )

    next_outcome = ResolutionOutcome.NO_MATCH


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

    assert body["outcome"] == "no_match"
    assert body["action"] == "created"
    assert body["override_applied"] is False
    assert body["entity"]["canonical_name"] == "Example Startup"
    assert body["entity"]["founding_year"] == 2024
    assert body["entity"]["stage"] == "pre_seed"
    assert body["entity"]["business_model"] == "b2b"
    assert body["entity"]["aliases"] == ["Example"]
    assert "id" in body["entity"]

    assert len(fake_service.calls) == 1
    assert fake_service.calls[0]["aliases"] == {"Example"}
    assert fake_service.calls[0]["allow_possible_duplicate"] is False


def test_possible_duplicate_blocks_unless_explicitly_overridden(setup_client):
    client, fake_service = setup_client
    fake_service.next_outcome = ResolutionOutcome.POSSIBLE_DUPLICATE
    payload = {
        "canonical_name": "Possible Startup",
        "founding_year": 2024,
        "stage": "pre_seed",
        "business_model": "b2b",
    }

    blocked = client.post("/api/v1/organisations/startups", json=payload)
    assert blocked.status_code == 409
    assert blocked.json()["action"] == "blocked"
    assert blocked.json()["entity"] is None
    assert blocked.json()["candidates_truncated"] is True

    overridden = client.post(
        "/api/v1/organisations/startups",
        json={**payload, "allow_possible_duplicate": True},
    )
    assert overridden.status_code == 201
    assert overridden.json()["outcome"] == "possible_duplicate"
    assert overridden.json()["action"] == "created"
    assert overridden.json()["override_applied"] is True


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
