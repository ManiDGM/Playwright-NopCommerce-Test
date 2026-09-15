"""URL path constants for admin ProductReview MVC/AJAX endpoints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductReviewsEndpoints:
    LIST_PAGE: str = "/Admin/ProductReview/List"
    LIST: str = "/Admin/ProductReview/List"
    EDIT_PAGE: str = "/Admin/ProductReview/Edit/{review_id}"
    EDIT: str = "/Admin/ProductReview/Edit"
    DELETE: str = "/Admin/ProductReview/Delete/{review_id}"
    APPROVE_SELECTED: str = "/Admin/ProductReview/ApproveSelected"
    DISAPPROVE_SELECTED: str = "/Admin/ProductReview/DisapproveSelected"
    DELETE_SELECTED: str = "/Admin/ProductReview/DeleteSelected"
    STOREFRONT_PRODUCT_REVIEWS: str = "/productreviews/{product_id}"

    @staticmethod
    def edit_page(review_id: int) -> str:
        return f"/Admin/ProductReview/Edit/{review_id}"

    @staticmethod
    def delete(review_id: int) -> str:
        return f"/Admin/ProductReview/Delete/{review_id}"

    @staticmethod
    def storefront_product_reviews(product_id: int) -> str:
        return f"/productreviews/{product_id}"


PRODUCT_REVIEWS_ENDPOINTS = ProductReviewsEndpoints()
