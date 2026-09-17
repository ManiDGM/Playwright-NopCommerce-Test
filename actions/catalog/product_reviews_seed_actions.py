"""Storefront seed helpers for product reviews (no admin Create)."""

from __future__ import annotations

import os

from playwright.sync_api import APIRequestContext, Page

from api.actions.catalog.product_reviews_actions import (
    ProductReviewsActions as ApiProductReviewsActions,
    unique_review_text,
    unique_review_title,
)


class ProductReviewsSeedActions:
    """
    Seed product reviews for admin moderation tests.

    Prefers storefront submission (admin Create does not exist). Creates a
    published product via API when the catalog has no reviews yet.
    """

    STOREFRONT_TITLE: str = "#AddProductReview_Title"
    STOREFRONT_REVIEW_TEXT: str = "#AddProductReview_ReviewText"
    STOREFRONT_RATING_5: str = "#addproductrating_5"
    STOREFRONT_SUBMIT: str = "#add-review"
    STOREFRONT_REVIEW_FORM: str = "#review-form"

    def __init__(
        self,
        page: Page | None = None,
        request: APIRequestContext | None = None,
        base_url: str | None = None,
        *,
        api_request_context: APIRequestContext | None = None,
    ) -> None:
        self.page = page
        resolved_request = request or api_request_context
        self.base_url = (
            base_url
            or os.environ.get("BASE_URL", "http://localhost:5000")
        ).rstrip("/")
        if resolved_request is None:
            raise ValueError("APIRequestContext is required for product review seeding")
        self.request = resolved_request
        self.api = ApiProductReviewsActions(resolved_request)

    def seed_unique_review(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
        product_id: int | None = None,
        use_ui: bool = False,
    ) -> tuple[int, str, str]:
        review_title = title or unique_review_title()
        text = review_text or unique_review_text()

        if use_ui and self.page is not None:
            return self._seed_via_storefront_ui(
                title=review_title,
                review_text=text,
                is_approved=is_approved,
                product_id=product_id,
            )

        return self.api.seed_unique_review(
            title=review_title,
            review_text=text,
            is_approved=is_approved,
            product_id=product_id,
        )

    def create_review_via_storefront(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
        product_id: int | None = None,
    ) -> str:
        """Seed a review and return its title (convenience for UI specs)."""
        _review_id, seeded_title, _text = self.seed_unique_review(
            title=title,
            review_text=review_text,
            is_approved=is_approved,
            product_id=product_id,
        )
        return seeded_title

    def _seed_via_storefront_ui(
        self,
        *,
        title: str,
        review_text: str,
        is_approved: bool,
        product_id: int | None,
    ) -> tuple[int, str, str]:
        assert self.page is not None

        resolved_product_id = self.api.resolve_or_create_product_id(product_id)
        se_name = self.api.client.get_product_se_name(resolved_product_id)
        if not se_name:
            raise RuntimeError(f"Could not resolve SeName for product {resolved_product_id}")

        self.page.goto(f"{self.base_url}/{se_name}")
        form = self.page.locator(self.STOREFRONT_REVIEW_FORM)
        form.wait_for(state="visible")
        self.page.locator(self.STOREFRONT_TITLE).fill(title)
        self.page.locator(self.STOREFRONT_REVIEW_TEXT).fill(review_text)
        self.page.locator(self.STOREFRONT_RATING_5).check()
        self.page.locator(self.STOREFRONT_SUBMIT).click()

        review_id = self.api.get_review_id_by_title(title)
        if review_id is None:
            raise RuntimeError(f"Storefront seed did not create review titled '{title}'")

        if is_approved:
            self.api.ensure_approved_review(review_id)
        else:
            self.api.ensure_disapproved_review(review_id)

        return review_id, title, review_text
