"""UI scenarios for admin Product review management."""

from __future__ import annotations

import json
import logging
import re

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


@pytest.fixture
def product_reviews_ui(page: Page, base_url: str) -> ProductReviewsActions:
    actions = ProductReviewsActions(page, base_url)
    actions.open_product_review_list()
    return actions


@pytest.fixture
def api_product_reviews(api_request_context) -> ApiProductReviewsActions:
    return ApiProductReviewsActions(api_request_context)


@pytest.fixture
def product_reviews_seed(
    page: Page,
    api_request_context,
    base_url: str,
) -> ProductReviewsSeedActions:
    return ProductReviewsSeedActions(
        page=page,
        request=api_request_context,
        base_url=base_url,
    )


@pytest.fixture(autouse=True)
def _teardown_to_product_review_list(product_reviews_ui: ProductReviewsActions):
    yield
    product_reviews_ui.navigate_to_product_review_list()


class TestProductReviews:
    def test_scenario_1_view_product_review_list(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
    ) -> None:
        log_data("Scenario", {"title": "Scenario 1: View the product review list"})
        review_id, title, _text = product_reviews_seed.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        expect(product_reviews_ui.page.locator(product_reviews_selectors.GRID)).to_be_visible()
        expect(product_reviews_ui.product_reviews_page.approve_selected_button()).to_be_visible()
        expect(product_reviews_ui.product_reviews_page.disapprove_selected_button()).to_be_visible()
        expect(product_reviews_ui.product_reviews_page.delete_selected_button()).to_be_visible()

    def test_scenario_2_search_product_reviews_by_text(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.search_by_text(title)
        log_data("Search term", title)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(title),
        ).to_be_visible()

    def test_scenario_3_edit_title_and_review_text(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        review_id, original_title, _text = product_reviews_seed.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": original_title})
        product_reviews_ui.open_product_review_list()

        new_title = product_reviews_ui.generate_unique_title("edited")
        new_review_text = product_reviews_ui.generate_unique_review_text("edited_text")
        log_data("Edit payload", {"Title": new_title, "ReviewText": new_review_text})

        product_reviews_ui.edit_title_and_review_text(
            original_title,
            new_title=new_title,
            new_review_text=new_review_text,
        )

        expect(product_reviews_ui.page).to_have_url(
            re.compile(r".*/Admin/ProductReview/List(?:\?.*)?$"),
        )
        expect(product_reviews_ui.product_reviews_page.success_alert()).to_be_visible()
        product_reviews_ui.search_by_text(new_title)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(new_title),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_4_reject_empty_title_on_edit(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.open_edit_and_clear_title(title)
        log_data("Edit payload", {"Title": ""})

        expect(product_reviews_ui.page).to_have_url(
            re.compile(r".*/Admin/ProductReview/Edit/\d+"),
        )
        expect(product_reviews_ui.product_reviews_page.title_validation_error()).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_5_reject_empty_review_text_on_edit(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.open_edit_and_clear_review_text(title)
        log_data("Edit payload", {"ReviewText": ""})

        expect(product_reviews_ui.page).to_have_url(
            re.compile(r".*/Admin/ProductReview/Edit/\d+"),
        )
        expect(
            product_reviews_ui.product_reviews_page.review_text_validation_error(),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_6_approve_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review(is_approved=False)
        log_data("Seeded disapproved review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.approve_selected_by_title(title)
        log_data("Approve selected title", title)

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.approved_icon_in_row(title),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_7_disapprove_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
        api_product_reviews: ApiProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review(is_approved=True)
        log_data("Seeded approved review", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.disapprove_selected_by_title(title)
        log_data("Disapprove selected title", title)

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.disapproved_icon_in_row(title),
        ).to_be_visible()

        api_product_reviews.delete_selected([review_id])

    def test_scenario_8_delete_selected_product_reviews(
        self,
        product_reviews_ui: ProductReviewsActions,
        product_reviews_seed: ProductReviewsSeedActions,
    ) -> None:
        review_id, title, _text = product_reviews_seed.seed_unique_review(
            title=product_reviews_ui.generate_unique_title("seed_delete"),
        )
        log_data("Seeded review for deletion", {"Id": review_id, "Title": title})
        product_reviews_ui.open_product_review_list()

        product_reviews_ui.delete_selected_by_title(title)
        log_data("Delete selected title", title)

        product_reviews_ui.search_by_text(title)
        expect(
            product_reviews_ui.product_reviews_page.row_containing_title(title),
        ).to_have_count(0)
