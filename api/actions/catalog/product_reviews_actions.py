"""Business flows for admin ProductReview API operations."""

from __future__ import annotations

import re
import uuid
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.actions.catalog.products_actions import ProductsActions
from api.clients.catalog.product_reviews_client import ProductReviewsClient
from api.types.catalog.product_reviews_types import (
    ProductReviewListResponse,
    ProductReviewPayload,
)


def unique_review_title(prefix: str = "auto_review") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def unique_review_text(prefix: str = "auto_review_text") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ProductReviewsActions:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request
        self.client = ProductReviewsClient(request)
        self._products = ProductsActions(request)

    def list(
        self,
        *,
        search_text: str = "",
        search_approved_id: int = 0,
        search_store_id: int = 0,
        search_product_id: int = 0,
        start: int = 0,
        length: int = 15,
        draw: str = "1",
    ) -> APIResponse:
        payload: ProductReviewPayload = {
            "draw": draw,
            "start": str(start),
            "length": str(length),
            "SearchText": search_text,
            "SearchStoreId": str(search_store_id),
            "SearchProductId": str(search_product_id),
            "SearchApprovedId": str(search_approved_id),
            "CreatedOnFrom": "",
            "CreatedOnTo": "",
        }
        return self.client.list_reviews(payload)

    def edit(
        self,
        review_id: int,
        *,
        title: str | None = None,
        review_text: str | None = None,
        reply_text: str | None = None,
        is_approved: bool | None = None,
        extra_fields: ProductReviewPayload | None = None,
    ) -> APIResponse:
        fields = self.get_edit_fields(review_id)
        payload: ProductReviewPayload = {
            "Id": str(review_id),
            "Title": fields["Title"] if title is None else title,
            "ReviewText": fields["ReviewText"] if review_text is None else review_text,
            "ReplyText": fields["ReplyText"] if reply_text is None else reply_text,
            "IsApproved": (
                fields["IsApproved"]
                if is_approved is None
                else ("true" if is_approved else "false")
            ),
            **(extra_fields or {}),
        }
        return self.client.edit_review(payload)

    def delete(self, review_id: int) -> APIResponse:
        return self.client.delete_review(review_id)

    def approve_selected(self, review_ids: list[int]) -> APIResponse:
        return self.client.approve_selected(review_ids)

    def disapprove_selected(self, review_ids: list[int]) -> APIResponse:
        return self.client.disapprove_selected(review_ids)

    def delete_selected(self, review_ids: list[int]) -> APIResponse:
        return self.client.delete_selected(review_ids)

    def ensure_disapproved_review(self, review_id: int) -> APIResponse:
        return self.disapprove_selected([review_id])

    def ensure_approved_review(self, review_id: int) -> APIResponse:
        return self.approve_selected([review_id])

    @staticmethod
    def parse_list_response(response: APIResponse) -> ProductReviewListResponse:
        return response.json()

    @staticmethod
    def find_review_id_by_title(
        list_body: ProductReviewListResponse,
        title: str,
    ) -> int | None:
        for row in list_body.get("Data", []):
            row_title = row.get("Title") or ""
            if title in row_title:
                review_id = row.get("Id")
                if review_id is not None:
                    return int(review_id)
        return None

    @staticmethod
    def find_review_row_by_title(
        list_body: ProductReviewListResponse,
        title: str,
    ) -> dict[str, Any] | None:
        for row in list_body.get("Data", []):
            row_title = row.get("Title") or ""
            if title in row_title:
                return dict(row)
        return None

    def get_first_review(self) -> dict[str, Any] | None:
        response = self.list(length=50)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        rows = body.get("Data") or []
        return dict(rows[0]) if rows else None

    def get_review_id_by_title(self, title: str) -> int | None:
        response = self.list(search_text=title, length=50)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        return self.find_review_id_by_title(body, title)

    def get_edit_fields(self, review_id: int) -> dict[str, str]:
        response = self.client.get_edit_page(review_id)
        if not response.ok:
            raise RuntimeError(
                f"Failed to open edit page for review {review_id}: HTTP {response.status}",
            )
        html = response.text()
        return {
            "Title": self._input_value(html, "Title"),
            "ReviewText": self._textarea_value(html, "ReviewText"),
            "ReplyText": self._textarea_value(html, "ReplyText"),
            "IsApproved": (
                "true" if self._checkbox_checked(html, "IsApproved") else "false"
            ),
        }

    def resolve_or_create_product_id(self, product_id: int | None = None) -> int:
        if product_id is not None:
            return product_id

        existing = self.get_first_review()
        if existing is not None and existing.get("ProductId") is not None:
            return int(existing["ProductId"])

        name, create_response = self._products.create_random(published=True)
        if create_response.status not in (200, 302):
            raise RuntimeError(
                f"Failed to create product for review seed: HTTP {create_response.status}",
            )
        created_id = self._products.get_product_id_by_name(name)
        if created_id is None:
            raise RuntimeError(f"Created product '{name}' not found in product list")
        return created_id

    def seed_unique_review(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
        product_id: int | None = None,
    ) -> tuple[int, str, str]:
        """Create a unique review via storefront POST (admin Create does not exist)."""
        review_title = title or unique_review_title()
        text = review_text or unique_review_text()
        resolved_product_id = self.resolve_or_create_product_id(product_id)

        response = self.client.add_storefront_review(
            resolved_product_id,
            title=review_title,
            review_text=text,
        )
        if response.status not in (200, 302):
            raise RuntimeError(
                f"Storefront review seed failed: HTTP {response.status} url={response.url}",
            )

        review_id = self.get_review_id_by_title(review_title)
        if review_id is None:
            raise RuntimeError(
                f"Storefront seed did not create review titled '{review_title}'",
            )

        if is_approved:
            self.ensure_approved_review(review_id)
        else:
            self.ensure_disapproved_review(review_id)

        return review_id, review_title, text

    def prepare_review_for_edit(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
        product_id: int | None = None,
    ) -> tuple[int, str, str]:
        """Ensure a searchable review exists via storefront seed (create product if needed)."""
        return self.seed_unique_review(
            title=title,
            review_text=review_text,
            is_approved=is_approved,
            product_id=product_id,
        )

    @staticmethod
    def _input_value(html: str, field_id: str) -> str:
        patterns = (
            rf'id=["\']{re.escape(field_id)}["\'][^>]*value=["\']([^"\']*)["\']',
            rf'value=["\']([^"\']*)["\'][^>]*id=["\']{re.escape(field_id)}["\']',
        )
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    @staticmethod
    def _textarea_value(html: str, field_id: str) -> str:
        match = re.search(
            rf'<textarea[^>]*id=["\']{re.escape(field_id)}["\'][^>]*>(.*?)</textarea>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    @staticmethod
    def _checkbox_checked(html: str, field_id: str) -> bool:
        match = re.search(
            rf'<input[^>]*id=["\']{re.escape(field_id)}["\'][^>]*>',
            html,
            re.IGNORECASE,
        )
        if not match:
            return False
        return "checked" in match.group(0).lower()
