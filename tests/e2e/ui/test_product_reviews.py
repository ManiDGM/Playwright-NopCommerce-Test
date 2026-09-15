"""UI scenarios for admin Product review management."""

from __future__ import annotations

import json
import logging

import pytest
from playwright.sync_api import Page, expect

from actions.catalog.product_reviews_actions import ProductReviewsActions
from actions.catalog.product_reviews_seed_actions import ProductReviewsSeedActions
from api.actions.catalog.product_reviews_actions import (
    ProductReviewsActions as ApiProductReviewsActions,
)
from selectors.catalog.product_reviews_selectors import product_reviews_selectors

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture(scope="module")
def product_reviews_ui(page: Page, base_url: str) -> ProductReviewsActions:
    actions = ProductReviewsActions(page, base_url)
    actions.open_product_review_list()
    return actions


@pytest.fixture(scope="module")
def api_product_reviews(api_request_context) -> ApiProductReviewsActions:
    return ApiProductReviewsActions(api_request_context)


@pytest.fixture(scope="module")
def product_reviews_seed(page: Page, base_url: str) -> ProductReviewsSeedActions:
    return ProductReviewsSeedActions(page, base_url)


class TestProductReviews:
    def teardown_method(self, product_reviews_ui: ProductReviewsActions) -> None:
        product_reviews_ui.navigate_to_product_review_list()

    def test_scenario_1_view_and_search_product_review_list(
        self,
        product_reviews_ui: ProductReviewsActions,
    ) -> None:
        log_data("Scenario", {"title": "View and search the product review list"})
        expect(product_reviews_ui.page.locator(product_reviews_selectors.GRID)).to_be_visible()

        search_term = product_reviews_selectors.SAMPLE_REVIEW_TITLE
        product_reviews_ui.search_by_text(search_term)
        log_data("Search term", search_term)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(search_term),
        ).to_be_visible()

    def test_scenario_2_edit_product_review_title_and_text(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        original_title = product_reviews_seed.create_review_via_storefront()
        log_data("Seeded review title", original_title)
        product_reviews_ui.open_product_review_list()

        new_title = product_reviews_ui.generate_unique_title("edited")
        new_review_text = f"Updated review text for {new_title}."
        log_data("Edit payload", {"Title": new_title, "ReviewText": new_review_text})

        product_reviews_ui.edit_review_content(
            original_title,
            new_title=new_title,
            new_review_text=new_review_text,
        )

        expect(product_reviews_ui.page).to_have_url(
            lambda url: "/Admin/ProductReview/List" in url,
        )
        expect(product_reviews_ui.product_reviews_page.success_alert()).to_be_visible()
        product_reviews_ui.search_by_text(new_title)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(new_title),
        ).to_be_visible()

        review_id = api_product_reviews.get_review_id_by_title(new_title)
        log_data("Created review id for cleanup", review_id)
        if review_id is not None:
            api_product_reviews.delete_selected([review_id])

    def test_scenario_3_reject_empty_title_on_edit(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        title = product_reviews_seed.create_review_via_storefront()
        log_data("Seeded review title", title)
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.submit_edit_with_empty_title(title)
        log_data("Edit payload", {"Title": ""})

        expect(product_reviews_ui.page).to_have_url(
            lambda url: "/Admin/ProductReview/Edit/" in url,
        )
        expect(product_reviews_ui.product_reviews_page.title_validation_error()).to_be_visible()

        review_id = api_product_reviews.get_review_id_by_title(title)
        if review_id is not None:
            api_product_reviews.delete_selected([review_id])

    def test_scenario_4_reject_empty_review_text_on_edit(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        title = product_reviews_seed.create_review_via_storefront()
        log_data("Seeded review title", title)
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.submit_edit_with_empty_review_text(title)
        log_data("Edit payload", {"ReviewText": ""})

        expect(product_reviews_ui.page).to_have_url(
            lambda url: "/Admin/ProductReview/Edit/" in url,
        )
        expect(
            product_reviews_ui.product_reviews_page.review_text_validation_error(),
        ).to_be_visible()

        review_id = api_product_reviews.get_review_id_by_title(title)
        if review_id is not None:
            api_product_reviews.delete_selected([review_id])

    def test_scenario_5_approve_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        title = product_reviews_seed.create_review_via_storefront()
        product_reviews_ui.open_product_review_list()
        review_id = api_product_reviews.get_review_id_by_title(title)
        assert review_id is not None, f"Review not found after seed: {title}"

        disapprove_response = api_product_reviews.ensure_disapproved_review(review_id)
        log_data("Disapprove seed status", disapprove_response.status)

        product_reviews_ui.approve_selected_reviews([title])
        log_data("Approve selected titles", [title])

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.approved_icon_in_row(title),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_6_disapprove_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        title = product_reviews_seed.create_review_via_storefront()
        product_reviews_ui.open_product_review_list()
        review_id = api_product_reviews.get_review_id_by_title(title)
        assert review_id is not None, f"Review not found after seed: {title}"
        log_data("Seeded approved review", {"Id": review_id, "Title": title})

        product_reviews_ui.disapprove_selected_reviews([title])
        log_data("Disapprove selected titles", [title])

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.disapproved_icon_in_row(title),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_7_delete_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
    ) -> None:
        title = product_reviews_seed.create_review_via_storefront()
        log_data("Seeded review title", title)
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.delete_selected_reviews([title])
        log_data("Delete selected titles", [title])

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(title),
        ).to_have_count(0)
