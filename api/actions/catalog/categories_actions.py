"""Business flows for admin Category API operations."""

from __future__ import annotations

import uuid
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.clients.catalog.categories_client import CategoriesClient
from api.types.catalog.categories_types import CategoryListResponse, CategoryPayload


def unique_category_name(prefix: str = "auto") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class CategoriesActions:
    DEFAULT_CREATE_FIELDS: dict[str, Any] = {
        "Name": "",
        "ParentCategoryId": "0",
        "CategoryTemplateId": "1",
        "PageSize": "5",
        "AllowCustomersToSelectPageSize": "false",
        "Published": "true",
        "DisplayOrder": "0",
        "ShowOnHomepage": "false",
        "PriceRangeFiltering": "false",
        "ManuallyPriceRange": "false",
        "PictureId": "0",
        "RestrictFromVendors": "false",
    }

    def __init__(self, request: APIRequestContext) -> None:
        self.client = CategoriesClient(request)

    def list(
        self,
        *,
        search_name: str = "",
        search_published_id: int = 0,
        search_store_id: int = 0,
        start: int = 0,
        length: int = 10,
        draw: str = "1",
    ) -> APIResponse:
        payload: CategoryPayload = {
            "draw": draw,
            "start": str(start),
            "length": str(length),
            "SearchCategoryName": search_name,
            "SearchPublishedId": str(search_published_id),
            "SearchStoreId": str(search_store_id),
        }
        return self.client.list_categories(payload)

    def create(
        self,
        name: str | None = None,
        *,
        published: bool = True,
        extra_fields: CategoryPayload | None = None,
    ) -> APIResponse:
        payload: CategoryPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Name": name or unique_category_name(),
            "Published": "true" if published else "false",
            **(extra_fields or {}),
        }
        return self.client.create_category(payload)

    def create_random(self, *, published: bool = True) -> tuple[str, APIResponse]:
        name = unique_category_name()
        response = self.create(name, published=published)
        return name, response

    def edit(self, category_id: int, name: str, **fields: Any) -> APIResponse:
        payload: CategoryPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Id": str(category_id),
            "Name": name,
            **{key: str(value) for key, value in fields.items()},
        }
        return self.client.edit_category(payload)

    def delete(self, category_id: int) -> APIResponse:
        return self.client.delete_category(category_id)

    def delete_selected(self, category_ids: list[int]) -> APIResponse:
        return self.client.delete_selected(category_ids)

    @staticmethod
    def parse_list_response(response: APIResponse) -> CategoryListResponse:
        return response.json()

    @staticmethod
    def find_category_id_by_name(
        list_body: CategoryListResponse,
        name: str,
    ) -> int | None:
        for row in list_body.get("Data", []):
            breadcrumb = row.get("Breadcrumb") or row.get("Name") or ""
            if name == breadcrumb or name in breadcrumb:
                category_id = row.get("Id")
                if category_id is not None:
                    return int(category_id)
        return None

    def get_category_id_by_name(self, name: str) -> int | None:
        response = self.list(search_name=name)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        return self.find_category_id_by_name(body, name)
