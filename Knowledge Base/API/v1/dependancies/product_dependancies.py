from infrastructure.database.connection import DatabaseManager
from application.services.product_service import ProductService
from repositories.product_repository import ProductRepository

def get_product_service() -> ProductService:

    product_repo = ProductRepository()
    database_manager = DatabaseManager()

    return ProductService(
        product_repository= product_repo,
        database_manager=database_manager,
    )
