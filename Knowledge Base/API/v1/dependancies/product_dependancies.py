from infrastructure.database.connection import DatabaseManager
from application.services.product_service import ProductService
from repositories.product_repository import ProductRepository
from API.v1.dependancies.identity_resolution_dependancies import get_identity_resolution_service

def get_product_service() -> ProductService:

    product_repo = ProductRepository()
    database_manager = DatabaseManager()

    return ProductService(
        product_repository= product_repo,
        database_manager=database_manager,
        identity_resolution_service=get_identity_resolution_service(),
    )
