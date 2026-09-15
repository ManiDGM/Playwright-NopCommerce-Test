"""Storefront seed helpers for product reviews (no admin Create)."""

from __future__ import annotations

import os

from playwright.sync_api import Page

from api.actions.catalog.product_reviews_actions import (
    ProductReviewsActions as ApiProductReviewsActions,
    unique_review_text,
    unique_review_title,
)
from playwright.sync_api import APIRequestContext


class ProductReviewsSeedActions:
    """
    Seed product reviews for admin moderation tests.

    Prefers storefront submission (admin Create does not exist). Falls back to
    retitling an existing sample-data review via the admin Edit API.
    """

    STOREFRONT_TITLE: str = "#AddProductReview_Title"
    STOREFRONT_REVIEW_TEXT: str = "#AddProductReview_ReviewText"
    STOREFRONT_RATING_5: str = "#addproductrating_5"
    STOREFRONT_SUBMIT: str = "#add-review"
    STOREFRONT_REVIEW_FORM: str = "#review-form"

    def __init__(
        self,
        *,
        page: Page | None = None,
        request: APIRequestContext | None = None,
        base_url: str | None = None,
    ) -> None:
        self.page = page
        self.request = request
        self.base_url = (
            base_url
            or os.environ.get("BASE_URL", "http://localhost:5000")
        ).rstrip("/")
        if request is None:
            raise ValueError("APIRequestContext is required for product review seeding")
        self.api = ApiProductReviewsActions(request)

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

        return self.api.prepare_review_for_edit(
            title=review_title,
            review_text=text,
            is_approved=is_approved,
        )

    def _seed_via_storefront_ui(
        self,
        *,
        title: str,
        review_text: str,
        is_approved: bool,
        product_id: int | None,
    ) -> tuple[int, str, str]:
        assert self.page is not None

        resolved_product_id = product_id
        if resolved_product_id is None:
            existing = self.api.get_first_review()
            if existing is None or existing.get("ProductId") is None:
                raise RuntimeError(
                    "No product reviews found to resolve ProductId for storefront seed.",
                )
            resolved_product_id = int(existing["ProductId"])

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

        if not is_approved:
            self.api.disapprove_selected([review_id])

        return review_id, title, review_text
