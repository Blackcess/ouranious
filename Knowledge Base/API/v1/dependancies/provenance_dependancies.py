"""Dependency factories for Provenance application services."""

from application.services.claim_service import ClaimService
from application.services.claim_materialisation_service import ClaimMaterialisationService
from application.services.identity_resolver import IdentityResolver
from application.services.identity_resolution_service import IdentityResolutionService
from application.services.relationship_resolution_service import RelationshipResolutionService
from application.services.source_service import SourceService
from application.services.verification_assessment_service import (
    VerificationAssessmentService,
)
from infrastructure.database.connection import DatabaseManager
from repositories.claim_repository import ClaimRepository
from repositories.claim_materialisation_repository import ClaimMaterialisationRepository
from repositories.industry_repository import IndustryRepository
from repositories.organisation_repository import OrganisationRepository
from repositories.person_repository import PersonRepository
from repositories.place_repository import PlaceRepository
from repositories.product_repository import ProductRepository
from repositories.relationship_repository import RelationshipRepository
from repositories.source_repository import SourceRepository
from repositories.verification_assessment_repository import (
    VerificationAssessmentRepository,
)
from repositories.technology_repository import TechnologyRepository
from domain_models.Identity_model.identity import IdentityKind

from API.v1.dependancies.identity_resolver_dependancies import get_identity_resolver


def get_source_service() -> SourceService:
    return SourceService(
        source_repository=SourceRepository(),
        database_manager=DatabaseManager(),
    )


def get_claim_service() -> ClaimService:
    return ClaimService(
        claim_repository=ClaimRepository(),
        database_manager=DatabaseManager(),
        identity_resolver=get_identity_resolver(),
        relationship_repository=RelationshipRepository(),
    )


def get_verification_assessment_service() -> VerificationAssessmentService:
    return VerificationAssessmentService(
        assessment_repository=VerificationAssessmentRepository(),
        claim_repository=ClaimRepository(),
        database_manager=DatabaseManager(),
    )


def get_claim_materialisation_service() -> ClaimMaterialisationService:
    people = PersonRepository()
    organisations = OrganisationRepository()
    places = PlaceRepository()
    industries = IndustryRepository()
    products = ProductRepository()
    technologies = TechnologyRepository()
    identity_resolver = IdentityResolver(
        person_repository=people,
        organisation_repository=organisations,
        place_repository=places,
        industry_repository=industries,
        product_repository=products,
        technology_repository=technologies,
        database_manager=DatabaseManager(),
    )
    relationship_repository = RelationshipRepository(
        person_repository=people,
        organisation_repository=organisations,
        place_repository=places,
        industry_repository=industries,
        product_repository=products,
        technology_repository=technologies,
    )
    identity_repositories = {
        IdentityKind.PERSON: people,
        IdentityKind.ORGANISATION: organisations,
        IdentityKind.PLACE: places,
        IdentityKind.INDUSTRY: industries,
        IdentityKind.PRODUCT: products,
        IdentityKind.TECHNOLOGY: technologies,
    }
    return ClaimMaterialisationService(
        claim_repository=ClaimRepository(),
        materialisation_repository=ClaimMaterialisationRepository(),
        identity_repositories=identity_repositories,
        relationship_repository=relationship_repository,
        identity_resolver=identity_resolver,
        identity_resolution_service=IdentityResolutionService(
            person_repository=people,
            organisation_repository=organisations,
            place_repository=places,
            industry_repository=industries,
            product_repository=products,
            technology_repository=technologies,
        ),
        relationship_resolution_service=RelationshipResolutionService(
            relationship_repository=relationship_repository,
            identity_resolver=identity_resolver,
            require_persisted_endpoints=True,
        ),
        database_manager=DatabaseManager(),
    )
