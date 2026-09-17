"""API scenarios for admin ProductReview MVC/AJAX endpoints."""

from __future__ import annotations

import json
import logging

import pytest
from playwright.sync_api import APIRequestContext

from api.actions.catalog.product_reviews_actions import (
    ProductReviewsActions,
    unique_review_title,
)
from api.endpoints.catalog.product_reviews_endpoints import PRODUCT_REVIEWS_ENDPOINTS

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture
def product_reviews_api(api_request_context: APIRequestContext) -> ProductReviewsActions:
    return ProductReviewsActions(api_request_context)


class TestProductReviewsApi:
    def test_scenario_1_list_product_reviews_returns_grid_data(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})

        response = product_reviews_api.list()
        body = product_reviews_api.parse_list_response(response)
        log_data("List response status", response.status)
        log_data("List response body", body)

        assert response.ok
        assert "Data" in body
        assert "recordsTotal" in body
        assert body.get("recordsTotal", 0) >= 1

    def test_scenario_2_search_product_reviews_by_text(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})

        response = product_reviews_api.list(search_text=title)
        body = product_reviews_api.parse_list_response(response)
        log_data("Search term", title)
        log_data("Search response status", response.status)
        log_data("Search response body", body)

        assert response.ok
        assert body.get("recordsFiltered", 0) >= 1
        matched_id = product_reviews_api.find_review_id_by_title(body, title)
        log_data("Matched review id", matched_id)
        assert matched_id == review_id

    def test_scenario_3_edit_product_review_title_and_text(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, original_title, original_text = product_reviews_api.seed_unique_review()
        log_data(
            "Seeded review",
            {"Id": review_id, "Title": original_title, "ReviewText": original_text},
        )
        original_fields = product_reviews_api.get_edit_fields(review_id)
        log_data("Original edit fields", original_fields)

        new_title = unique_review_title("api_edit")
        new_review_text = "Updated via API automation."
        edit_payload = {
            "Id": str(review_id),
            "Title": new_title,
            "ReviewText": new_review_text,
        }
        log_data("Edit request payload", edit_payload)

        edit_response = product_reviews_api.edit(
            review_id,
            title=new_title,
            review_text=new_review_text,
        )
        log_data("Edit response status", edit_response.status)
        log_data("Edit response url", edit_response.url)

        assert edit_response.status in (200, 302)
        assert "/Admin/ProductReview/List" in edit_response.url

        updated_list = product_reviews_api.parse_list_response(
            product_reviews_api.list(search_text=new_title),
        )
        log_data("Post-edit list body", updated_list)
        assert product_reviews_api.find_review_id_by_title(updated_list, new_title) == review_id

        restore_response = product_reviews_api.edit(
            review_id,
            title=original_fields.get("Title", original_title),
            review_text=original_fields.get("ReviewText", original_text),
            reply_text=original_fields.get("ReplyText", ""),
            is_approved=original_fields.get("IsApproved", "false") == "true",
        )
        log_data("Restore edit status", restore_response.status)

    def test_scenario_4_reject_empty_title_on_edit(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})

        log_data("Edit request payload", {"Id": review_id, "Title": ""})
        response = product_reviews_api.edit(review_id, title="")
        response_text = response.text()
        log_data("Edit response status", response.status)
        log_data("Edit response url", response.url)

        assert response.status == 200
        assert "/Admin/ProductReview/Edit" in response.url
        assert 'data-valmsg-for="Title"' in response_text
        assert "field-validation-error" in response_text
        assert "Title is required." in response_text

    def test_scenario_5_reject_empty_review_text_on_edit(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review()
        log_data("Seeded review", {"Id": review_id, "Title": title})

        log_data("Edit request payload", {"Id": review_id, "ReviewText": ""})
        response = product_reviews_api.edit(review_id, review_text="")
        response_text = response.text()
        log_data("Edit response status", response.status)
        log_data("Edit response url", response.url)

        assert response.status == 200
        assert "/Admin/ProductReview/Edit" in response.url
        assert 'data-valmsg-for="ReviewText"' in response_text
        assert "field-validation-error" in response_text
        assert "Review text is required." in response_text

    def test_scenario_6_approve_selected_product_reviews(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review(is_approved=False)
        log_data("Seeded disapproved review", {"Id": review_id, "Title": title})

        response = product_reviews_api.approve_selected([review_id])
        raw = response.text()
        body = response.json() if raw.strip() else {}
        log_data("ApproveSelected response status", response.status)
        log_data("ApproveSelected response body", body if raw.strip() else raw)

        assert response.status in (200, 204)
        if raw.strip():
            assert body.get("Result") is True

        approved_list = product_reviews_api.parse_list_response(
            product_reviews_api.list(search_text=title, search_approved_id=1),
        )
        log_data("Post-approve filtered list", approved_list)
        assert product_reviews_api.find_review_id_by_title(approved_list, title) == review_id

    def test_scenario_7_disapprove_selected_product_reviews(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review(is_approved=True)
        log_data("Seeded approved review", {"Id": review_id, "Title": title})

        response = product_reviews_api.disapprove_selected([review_id])
        raw = response.text()
        body = response.json() if raw.strip() else {}
        log_data("DisapproveSelected response status", response.status)
        log_data("DisapproveSelected response body", body if raw.strip() else raw)

        assert response.status in (200, 204)
        if raw.strip():
            assert body.get("Result") is True

        disapproved_list = product_reviews_api.parse_list_response(
            product_reviews_api.list(search_text=title, search_approved_id=2),
        )
        log_data("Post-disapprove filtered list", disapproved_list)
        assert product_reviews_api.find_review_id_by_title(disapproved_list, title) == review_id

        approve_response = product_reviews_api.approve_selected([review_id])
        log_data("Restore approve status", approve_response.status)

    def test_scenario_8_delete_selected_product_reviews(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        review_id, title, _text = product_reviews_api.seed_unique_review(
            title=unique_review_title("seed_delete"),
        )
        log_data("Seeded disposable review", {"Id": review_id, "Title": title})

        response = product_reviews_api.delete_selected([review_id])
        raw = response.text()
        body = response.json() if raw.strip() else {}
        log_data("DeleteSelected response status", response.status)
        log_data("DeleteSelected response body", body if raw.strip() else raw)

        assert response.status in (200, 204)
        if raw.strip():
            assert body.get("Result") is True

        remaining = product_reviews_api.parse_list_response(
            product_reviews_api.list(search_text=title),
        )
        log_data("Post-delete list body", remaining)
        assert product_reviews_api.find_review_id_by_title(remaining, title) is None

    def test_list_page_is_reachable(
        self,
        product_reviews_api: ProductReviewsActions,
    ) -> None:
        response = product_reviews_api.client.get_list_page()
        log_data("List page status", response.status)
        assert response.ok
        assert PRODUCT_REVIEWS_ENDPOINTS.LIST_PAGE in response.url
