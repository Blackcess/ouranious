from fastapi import APIRouter
from API.v1.organisations_routes.organisation import router as organisation_router
from API.v1.place_routes.place import router as place_router
from API.v1.person_routes.person import router as person_router
from API.v1.industry_routes.industry import router as industry_router
from API.v1.product_routes.product import router as product_router
from API.v1.technology_routes.technology import router as technology_router
from API.v1.relationships_routes.relationships import router as relationship_router
from API.v1.provenance_routes import router as provenance_router

router = APIRouter()

router.include_router(organisation_router)
router.include_router(place_router)
router.include_router(person_router)
router.include_router(industry_router)
router.include_router(product_router)
router.include_router(technology_router)
router.include_router(relationship_router)
router.include_router(provenance_router)





