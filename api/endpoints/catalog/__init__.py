"""Catalog API endpoint constants."""

from api.endpoints.catalog.categories_endpoints import (
    CATEGORIES_ENDPOINTS,
    CategoriesEndpoints,
)
from api.endpoints.catalog.manufacturers_endpoints import (
    MANUFACTURERS_ENDPOINTS,
    ManufacturersEndpoints,
)
from api.endpoints.catalog.product_reviews_endpoints import (
    PRODUCT_REVIEWS_ENDPOINTS,
    ProductReviewsEndpoints,
)
from api.endpoints.catalog.products_endpoints import (
    PRODUCTS_ENDPOINTS,
    ProductsEndpoints,
)

__all__ = [
    "CATEGORIES_ENDPOINTS",
    "MANUFACTURERS_ENDPOINTS",
    "PRODUCT_REVIEWS_ENDPOINTS",
    "PRODUCTS_ENDPOINTS",
    "CategoriesEndpoints",
    "ManufacturersEndpoints",
    "ProductReviewsEndpoints",
    "ProductsEndpoints",
]
