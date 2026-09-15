"""Catalog feature UI actions."""

from actions.catalog.categories_actions import CategoriesActions
from actions.catalog.manufacturers_actions import ManufacturersActions
from actions.catalog.product_reviews_actions import ProductReviewsActions
from actions.catalog.product_reviews_seed_actions import ProductReviewsSeedActions
from actions.catalog.products_actions import ProductsActions

__all__ = [
    "CategoriesActions",
    "ManufacturersActions",
    "ProductReviewsActions",
    "ProductReviewsSeedActions",
    "ProductsActions",
]
