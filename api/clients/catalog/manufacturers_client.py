"""HTTP client for admin Manufacturer MVC/AJAX endpoints."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.endpoints.catalog.manufacturers_endpoints import MANUFACTURERS_ENDPOINTS
from api.types.catalog.manufacturers_types import ManufacturerPayload
from support.session_helpers import (
    attach_antiforgery_token,
    fetch_antiforgery_token,
)


class ManufacturersClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _fetch_token(self, page_url: str = MANUFACTURERS_ENDPOINTS.LIST_PAGE) -> str:
        return fetch_antiforgery_token(self.request, page_url)

    def get_list_page(self) -> APIResponse:
        return self.request.get(MANUFACTURERS_ENDPOINTS.LIST_PAGE)

    def get_create_page(self) -> APIResponse:
        return self.request.get(MANUFACTURERS_ENDPOINTS.CREATE_PAGE)

    def get_edit_page(self, manufacturer_id: int) -> APIResponse:
        return self.request.get(MANUFACTURERS_ENDPOINTS.edit_page(manufacturer_id))

    def list_manufacturers(self, payload: ManufacturerPayload | None = None) -> APIResponse:
        token = self._fetch_token()
        form = attach_antiforgery_token(
            {
                "draw": "1",
                "start": "0",
                "length": "10",
                "SearchManufacturerName": "",
                "SearchPublishedId": "0",
                "SearchStoreId": "0",
                **(payload or {}),
            },
            token,
        )
        return self.request.post(MANUFACTURERS_ENDPOINTS.LIST, form=form)

    def create_manufacturer(self, payload: ManufacturerPayload) -> APIResponse:
        token = self._fetch_token(MANUFACTURERS_ENDPOINTS.CREATE_PAGE)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(MANUFACTURERS_ENDPOINTS.CREATE, form=form)

    def edit_manufacturer(self, payload: ManufacturerPayload) -> APIResponse:
        manufacturer_id = payload.get("Id")
        page_url = (
            MANUFACTURERS_ENDPOINTS.edit_page(int(manufacturer_id))
            if manufacturer_id is not None
            else MANUFACTURERS_ENDPOINTS.LIST_PAGE
        )
        token = self._fetch_token(page_url)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(MANUFACTURERS_ENDPOINTS.EDIT, form=form)

    def delete_manufacturer(self, manufacturer_id: int) -> APIResponse:
        token = self._fetch_token(MANUFACTURERS_ENDPOINTS.edit_page(manufacturer_id))
        form = attach_antiforgery_token({}, token)
        return self.request.post(MANUFACTURERS_ENDPOINTS.delete(manufacturer_id), form=form)

    def delete_selected(self, selected_ids: list[int]) -> APIResponse:
        token = self._fetch_token()
        data: dict[str, Any] = attach_antiforgery_token({}, token)
        for manufacturer_id in selected_ids:
            data.setdefault("selectedIds", [])
            if isinstance(data["selectedIds"], list):
                data["selectedIds"].append(str(manufacturer_id))
        return self.request.post(
            MANUFACTURERS_ENDPOINTS.DELETE_SELECTED,
            form=data,
        )
