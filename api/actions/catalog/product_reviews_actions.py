"""Business flows for admin ProductReview API operations."""

from __future__ import annotations

import uuid
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

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
        self.client = ProductReviewsClient(request)

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
        title: str,
        review_text: str,
        reply_text: str = "",
        is_approved: bool = True,
        extra_fields: ProductReviewPayload | None = None,
    ) -> APIResponse:
        payload: ProductReviewPayload = {
            "Id": str(review_id),
            "Title": title,
            "ReviewText": review_text,
            "ReplyText": reply_text,
            "IsApproved": "true" if is_approved else "false",
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
        response = self.list(search_text=title)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        return self.find_review_id_by_title(body, title)

    def seed_unique_review(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
        product_id: int | None = None,
    ) -> tuple[str, str, APIResponse]:
        """
        Create a unique review via storefront POST (no admin Create).

        Uses an existing review's ProductId when product_id is omitted (sample data).
        """
        review_title = title or unique_review_title()
        text = review_text or unique_review_text()

        resolved_product_id = product_id
        if resolved_product_id is None:
            existing = self.get_first_review()
            if existing is None or existing.get("ProductId") is None:
                raise RuntimeError(
                    "No product reviews found to resolve ProductId. "
                    "Install sample data or pass product_id.",
                )
            resolved_product_id = int(existing["ProductId"])

        response = self.client.add_storefront_review(
            resolved_product_id,
            title=review_title,
            review_text=text,
        )
        if response.status not in (200, 302):
            return review_title, text, response

        if not is_approved:
            review_id = self.get_review_id_by_title(review_title)
            if review_id is not None:
                self.disapprove_selected([review_id])

        return review_title, text, response

    def prepare_review_for_edit(
        self,
        *,
        title: str | None = None,
        review_text: str | None = None,
        is_approved: bool = True,
    ) -> tuple[int, str, str]:
        """
        Ensure a searchable review exists: prefer storefront seed, else retitle sample row.
        """
        review_title = title or unique_review_title()
        text = review_text or unique_review_text()

        try:
            seeded_title, seeded_text, seed_response = self.seed_unique_review(
                title=review_title,
                review_text=text,
                is_approved=is_approved,
            )
            if seed_response.status in (200, 302):
                review_id = self.get_review_id_by_title(seeded_title)
                if review_id is not None:
                    return review_id, seeded_title, seeded_text
        except RuntimeError:
            pass

        existing = self.get_first_review()
        if existing is None or existing.get("Id") is None:
            raise RuntimeError(
                "No product reviews available. Install nopCommerce sample data "
                "or seed via storefront.",
            )

        review_id = int(existing["Id"])
        edit_response = self.edit(
            review_id,
            title=review_title,
            review_text=text,
            reply_text=str(existing.get("ReplyText") or ""),
            is_approved=is_approved,
        )
        if edit_response.status not in (200, 302):
            raise RuntimeError(
                f"Failed to prepare review {review_id} for edit: HTTP {edit_response.status}",
            )
        return review_id, review_title, text
