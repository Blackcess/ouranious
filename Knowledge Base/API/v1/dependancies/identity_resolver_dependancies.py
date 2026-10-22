
from application.services.identity_resolver import IdentityResolver
import repositories as repo 
from infrastructure.database.connection import DatabaseManager


def get_identity_resolver() -> IdentityResolver:
    return IdentityResolver(
        person_repository= repo.person_repository.PersonRepository(),
        organisation_repository= repo.organisation_repository.OrganisationRepository(),
        place_repository= repo.place_repository.PlaceRepository() ,
        industry_repository= repo.industry_repository.IndustryRepository(),
        technology_repository= repo.technology_repository.TechnologyRepository(),
        product_repository= repo.product_repository.ProductRepository(), 
        database_manager= DatabaseManager(),
    )
