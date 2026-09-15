"""HTTP client for admin Product MVC/AJAX endpoints."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.endpoints.catalog.products_endpoints import PRODUCTS_ENDPOINTS
from api.types.catalog.products_types import ProductPayload
from support.session_helpers import (
    attach_antiforgery_token,
    fetch_antiforgery_token,
)


class ProductsClient:
    def __init__(self, request: APIRequestContext) -> None:
        self.request = request

    def _fetch_token(self, page_url: str = PRODUCTS_ENDPOINTS.LIST_PAGE) -> str:
        return fetch_antiforgery_token(self.request, page_url)

    def get_list_page(self) -> APIResponse:
        return self.request.get(PRODUCTS_ENDPOINTS.LIST_PAGE)

    def get_create_page(self) -> APIResponse:
        return self.request.get(PRODUCTS_ENDPOINTS.CREATE_PAGE)

    def get_edit_page(self, product_id: int) -> APIResponse:
        return self.request.get(PRODUCTS_ENDPOINTS.edit_page(product_id))

    def list_products(self, payload: ProductPayload | None = None) -> APIResponse:
        token = self._fetch_token()
        form = attach_antiforgery_token(
            {
                "draw": "1",
                "start": "0",
                "length": "10",
                "SearchProductName": "",
                "SearchCategoryId": "0",
                "SearchIncludeSubCategories": "false",
                "SearchManufacturerId": "0",
                "SearchStoreId": "0",
                "SearchWarehouseId": "0",
                "SearchVendorId": "0",
                "SearchProductTypeId": "0",
                "SearchPublishedId": "0",
                **(payload or {}),
            },
            token,
        )
        return self.request.post(PRODUCTS_ENDPOINTS.PRODUCT_LIST, form=form)

    def create_product(self, payload: ProductPayload) -> APIResponse:
        token = self._fetch_token(PRODUCTS_ENDPOINTS.CREATE_PAGE)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(PRODUCTS_ENDPOINTS.CREATE, form=form)

    def edit_product(self, payload: ProductPayload) -> APIResponse:
        product_id = payload.get("Id")
        page_url = (
            PRODUCTS_ENDPOINTS.edit_page(int(product_id))
            if product_id is not None
            else PRODUCTS_ENDPOINTS.LIST_PAGE
        )
        token = self._fetch_token(page_url)
        form = attach_antiforgery_token(payload, token)
        return self.request.post(PRODUCTS_ENDPOINTS.EDIT, form=form)

    def delete_product(self, product_id: int) -> APIResponse:
        token = self._fetch_token(PRODUCTS_ENDPOINTS.edit_page(product_id))
        form = attach_antiforgery_token({}, token)
        return self.request.post(PRODUCTS_ENDPOINTS.delete(product_id), form=form)

    def delete_selected(self, selected_ids: list[int]) -> APIResponse:
        token = self._fetch_token()
        data: dict[str, Any] = attach_antiforgery_token({}, token)
        for product_id in selected_ids:
            data.setdefault("selectedIds", [])
            if isinstance(data["selectedIds"], list):
                data["selectedIds"].append(str(product_id))
        return self.request.post(
            PRODUCTS_ENDPOINTS.DELETE_SELECTED,
            form=data,
        )

    def go_to_sku(self, sku: str) -> APIResponse:
        token = self._fetch_token()
        form = attach_antiforgery_token(
            {
                "GoDirectlyToSku": sku,
                "go-to-product-by-sku": "Go",
            },
            token,
        )
        return self.request.post(PRODUCTS_ENDPOINTS.GO_TO_SKU, form=form)
