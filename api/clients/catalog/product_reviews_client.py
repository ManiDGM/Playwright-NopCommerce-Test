"""HTTP client for admin ProductReview MVC/AJAX endpoints."""

from __future__ import annotations

import re
from urllib.parse import urlencode, urlparse

from playwright.sync_api import APIRequestContext, APIResponse

from api.endpoints.catalog.product_reviews_endpoints import PRODUCT_REVIEWS_ENDPOINTS
from api.types.catalog.product_reviews_types import ProductReviewPayload
from support.session_helpers import (
    ANTIFORGERY_TOKEN_NAME,
    attach_antiforgery_token,
    extract_antiforgery_token,
    fetch_antiforgery_token,
)


class ProductReviewsClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _fetch_token(self, page_url: str = PRODUCT_REVIEWS_ENDPOINTS.LIST_PAGE) -> str:
        return fetch_antiforgery_token(self.request, page_url)

    def get_list_page(self) -> APIResponse:
        return self.request.get(PRODUCT_REVIEWS_ENDPOINTS.LIST_PAGE)

    def get_edit_page(self, review_id: int) -> APIResponse:
        return self.request.get(PRODUCT_REVIEWS_ENDPOINTS.edit_page(review_id))

    def list_reviews(self, payload: ProductReviewPayload | None = None) -> APIResponse:
        token = self._fetch_token()
        form = attach_antiforgery_token(
            {
                "draw": "1",
                "start": "0",
                "length": "15",
                "SearchText": "",
                "SearchStoreId": "0",
                "SearchProductId": "0",
                "SearchApprovedId": "0",
                "CreatedOnFrom": "",
                "CreatedOnTo": "",
                **(payload or {}),
            },
            token,
        )
        return self.request.post(PRODUCT_REVIEWS_ENDPOINTS.LIST, form=form)

    def edit_review(self, payload: ProductReviewPayload) -> APIResponse:
        review_id = payload.get("Id")
        page_url = (
            PRODUCT_REVIEWS_ENDPOINTS.edit_page(int(review_id))
            if review_id is not None
            else PRODUCT_REVIEWS_ENDPOINTS.LIST_PAGE
        )
        token = self._fetch_token(page_url)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(PRODUCT_REVIEWS_ENDPOINTS.EDIT, form=form)

    def delete_review(self, review_id: int) -> APIResponse:
        token = self._fetch_token(PRODUCT_REVIEWS_ENDPOINTS.edit_page(review_id))
        form = attach_antiforgery_token({}, token)
        return self.request.post(PRODUCT_REVIEWS_ENDPOINTS.delete(review_id), form=form)

    def _post_selected(self, endpoint: str, selected_ids: list[int]) -> APIResponse:
        """POST selected-ids actions with repeated selectedIds (ASP.NET collection binding)."""
        token = self._fetch_token()
        fields: list[tuple[str, str]] = [(ANTIFORGERY_TOKEN_NAME, token)]
        fields.extend(("selectedIds", str(review_id)) for review_id in selected_ids)
        return self.request.post(
            endpoint,
            data=urlencode(fields),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def approve_selected(self, selected_ids: list[int]) -> APIResponse:
        return self._post_selected(PRODUCT_REVIEWS_ENDPOINTS.APPROVE_SELECTED, selected_ids)

    def disapprove_selected(self, selected_ids: list[int]) -> APIResponse:
        return self._post_selected(PRODUCT_REVIEWS_ENDPOINTS.DISAPPROVE_SELECTED, selected_ids)

    def delete_selected(self, selected_ids: list[int]) -> APIResponse:
        return self._post_selected(PRODUCT_REVIEWS_ENDPOINTS.DELETE_SELECTED, selected_ids)

    def get_product_se_name(self, product_id: int) -> str | None:
        response = self.request.get(f"/Admin/Product/Edit/{product_id}")
        if not response.ok:
            return None
        match = re.search(
            r'id=["\']SeName["\'][^>]*value=["\']([^"\']+)["\']',
            response.text(),
            re.IGNORECASE,
        )
        if match:
            return match.group(1)
        match = re.search(
            r'value=["\']([^"\']+)["\'][^>]*id=["\']SeName["\']',
            response.text(),
            re.IGNORECASE,
        )
        return match.group(1) if match else None

    def add_storefront_review(
        self,
        product_id: int,
        *,
        title: str,
        review_text: str,
        rating: int = 5,
        se_name: str | None = None,
    ) -> APIResponse:
        slug = se_name or self.get_product_se_name(product_id)
        if not slug:
            raise RuntimeError(f"Could not resolve SeName for product {product_id}")

        page_response = self.request.get(f"/{slug}")
        if not page_response.ok:
            raise RuntimeError(
                f"Failed to open storefront product page /{slug}: HTTP {page_response.status}",
            )
        html = page_response.text()
        if 'id="review-form"' not in html and "id='review-form'" not in html:
            raise RuntimeError(
                f"Storefront review form not available on /{slug} "
                "(product may disallow reviews or customer cannot leave a review)",
            )
        token = extract_antiforgery_token(html)
        action_path = self._extract_review_form_action(html) or (
            f"/Product/ProductReviews/{product_id}"
        )
        form = attach_antiforgery_token(
            {
                "ProductId": str(product_id),
                "AddProductReview.Title": title,
                "AddProductReview.ReviewText": review_text,
                "AddProductReview.Rating": str(rating),
            },
            token,
        )
        return self.request.post(action_path, form=form)

    @staticmethod
    def _extract_review_form_action(html: str) -> str | None:
        match = re.search(
            r'id=["\']review-form["\'][\s\S]{0,800}?<form[^>]*action=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if not match:
            match = re.search(
                r'<form[^>]*action=["\']([^"\']*ProductReviews[^"\']*)["\']',
                html,
                re.IGNORECASE,
            )
        if not match:
            return None
        action = match.group(1).strip()
        parsed = urlparse(action)
        if parsed.scheme and parsed.netloc:
            return parsed.path + (f"?{parsed.query}" if parsed.query else "")
        return action
