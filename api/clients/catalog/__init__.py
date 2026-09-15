"""Catalog API clients."""

from api.clients.catalog.categories_client import CategoriesClient
from api.clients.catalog.manufacturers_client import ManufacturersClient
from api.clients.catalog.product_reviews_client import ProductReviewsClient
from api.clients.catalog.products_client import ProductsClient

__all__ = [
    "CategoriesClient",
    "ManufacturersClient",
    "ProductReviewsClient",
    "ProductsClient",
]
