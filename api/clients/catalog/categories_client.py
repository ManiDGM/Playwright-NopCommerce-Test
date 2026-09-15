"""HTTP client for admin Category MVC/AJAX endpoints."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.endpoints.catalog.categories_endpoints import CATEGORIES_ENDPOINTS
from api.types.catalog.categories_types import CategoryPayload
from support.session_helpers import (
    attach_antiforgery_token,
    fetch_antiforgery_token,
)


class CategoriesClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _fetch_token(self, page_url: str = CATEGORIES_ENDPOINTS.LIST_PAGE) -> str:
        return fetch_antiforgery_token(self.request, page_url)

    def get_list_page(self) -> APIResponse:
        return self.request.get(CATEGORIES_ENDPOINTS.LIST_PAGE)

    def get_create_page(self) -> APIResponse:
        return self.request.get(CATEGORIES_ENDPOINTS.CREATE_PAGE)

    def get_edit_page(self, category_id: int) -> APIResponse:
        return self.request.get(CATEGORIES_ENDPOINTS.edit_page(category_id))

    def list_categories(self, payload: CategoryPayload | None = None) -> APIResponse:
        token = self._fetch_token()
        form = attach_antiforgery_token(
            {
                "draw": "1",
                "start": "0",
                "length": "10",
                "SearchCategoryName": "",
                "SearchPublishedId": "0",
                "SearchStoreId": "0",
                **(payload or {}),
            },
            token,
        )
        return self.request.post(CATEGORIES_ENDPOINTS.LIST, form=form)

    def create_category(self, payload: CategoryPayload) -> APIResponse:
        token = self._fetch_token(CATEGORIES_ENDPOINTS.CREATE_PAGE)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(CATEGORIES_ENDPOINTS.CREATE, form=form)

    def edit_category(self, payload: CategoryPayload) -> APIResponse:
        category_id = payload.get("Id")
        page_url = (
            CATEGORIES_ENDPOINTS.edit_page(int(category_id))
            if category_id is not None
            else CATEGORIES_ENDPOINTS.LIST_PAGE
        )
        token = self._fetch_token(page_url)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(CATEGORIES_ENDPOINTS.EDIT, form=form)

    def delete_category(self, category_id: int) -> APIResponse:
        token = self._fetch_token(CATEGORIES_ENDPOINTS.edit_page(category_id))
        form = attach_antiforgery_token({}, token)
        return self.request.post(CATEGORIES_ENDPOINTS.delete(category_id), form=form)

    def delete_selected(self, selected_ids: list[int]) -> APIResponse:
        token = self._fetch_token()
        data: dict[str, Any] = attach_antiforgery_token({}, token)
        data["selectedIds"] = [str(category_id) for category_id in selected_ids]
        return self.request.post(
            CATEGORIES_ENDPOINTS.DELETE_SELECTED,
            form=data,
        )
