"""Provenance API route collection."""

from fastapi import APIRouter

from API.v1.provenance_routes.assessments import router as assessments_router
from API.v1.provenance_routes.claims import router as claims_router
from API.v1.provenance_routes.materialisations import router as materialisations_router
from API.v1.provenance_routes.sources import router as sources_router

router = APIRouter()
router.include_router(sources_router)
router.include_router(claims_router)
router.include_router(materialisations_router)
router.include_router(assessments_router)
