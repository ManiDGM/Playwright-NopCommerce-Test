"""Business flows for admin Product API operations."""

from __future__ import annotations

import uuid
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.clients.catalog.products_client import ProductsClient
from api.types.catalog.products_types import ProductListResponse, ProductPayload


def unique_product_name(prefix: str = "auto") -> str:
    return f"{prefix}_{uuid.uuid4()}"


def unique_product_sku(prefix: str = "sku") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ProductsActions:
    """Defaults align with ProductModelFactory PrepareProductModelAsync for new products."""

    DEFAULT_CREATE_FIELDS: dict[str, Any] = {
        "ProductTypeId": "5",
        "ProductTemplateId": "1",
        "VisibleIndividually": "true",
        "Published": "true",
        "AllowCustomerReviews": "true",
        "IsShipEnabled": "true",
        "StockQuantity": "10000",
        "OrderMinimumQuantity": "1",
        "OrderMaximumQuantity": "10000",
        "NotifyAdminForQuantityBelow": "1",
        "MaxNumberOfDownloads": "10",
        "UnlimitedDownloads": "true",
        "RecurringCycleLength": "100",
        "RecurringTotalCycles": "10",
        "RentalPriceLength": "1",
        "MaximumCustomerEnteredPrice": "1000",
        "ManageInventoryMethodId": "0",
        "VendorId": "0",
        "TaxCategoryId": "0",
    }

    def __init__(self, request: APIRequestContext) -> None:
        self.client = ProductsClient(request)

    def list(
        self,
        *,
        search_name: str = "",
        search_published_id: int = 0,
        search_category_id: int = 0,
        search_manufacturer_id: int = 0,
        search_store_id: int = 0,
        search_warehouse_id: int = 0,
        search_vendor_id: int = 0,
        search_product_type_id: int = 0,
        start: int = 0,
        length: int = 10,
        draw: str = "1",
    ) -> APIResponse:
        payload: ProductPayload = {
            "draw": draw,
            "start": str(start),
            "length": str(length),
            "SearchProductName": search_name,
            "SearchCategoryId": str(search_category_id),
            "SearchIncludeSubCategories": "false",
            "SearchManufacturerId": str(search_manufacturer_id),
            "SearchStoreId": str(search_store_id),
            "SearchWarehouseId": str(search_warehouse_id),
            "SearchVendorId": str(search_vendor_id),
            "SearchProductTypeId": str(search_product_type_id),
            "SearchPublishedId": str(search_published_id),
        }
        return self.client.list_products(payload)

    def create(
        self,
        name: str | None = None,
        *,
        sku: str | None = None,
        published: bool = True,
        extra_fields: ProductPayload | None = None,
    ) -> APIResponse:
        # Preserve empty string so validation scenarios can POST Name=""
        payload: ProductPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Name": unique_product_name() if name is None else name,
            "Published": "true" if published else "false",
            **(extra_fields or {}),
        }
        if sku is not None:
            payload["Sku"] = sku
        return self.client.create_product(payload)

    def create_random(
        self,
        *,
        published: bool = True,
        with_sku: bool = False,
    ) -> tuple[str, APIResponse]:
        name = unique_product_name()
        sku = unique_product_sku() if with_sku else None
        response = self.create(name, sku=sku, published=published)
        return name, response

    def create_random_with_sku(self, *, published: bool = True) -> tuple[str, str, APIResponse]:
        name = unique_product_name()
        sku = unique_product_sku()
        response = self.create(name, sku=sku, published=published)
        return name, sku, response

    def edit(
        self,
        product_id: int,
        name: str,
        *,
        stock_quantity: int = 10000,
        **fields: Any,
    ) -> APIResponse:
        payload: ProductPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Id": str(product_id),
            "Name": name,
            "StockQuantity": str(stock_quantity),
            "LastStockQuantity": str(stock_quantity),
            **{key: str(value) for key, value in fields.items()},
        }
        return self.client.edit_product(payload)

    def delete(self, product_id: int) -> APIResponse:
        return self.client.delete_product(product_id)

    def delete_selected(self, product_ids: list[int]) -> APIResponse:
        return self.client.delete_selected(product_ids)

    def go_to_sku(self, sku: str) -> APIResponse:
        return self.client.go_to_sku(sku)

    @staticmethod
    def parse_list_response(response: APIResponse) -> ProductListResponse:
        return response.json()

    @staticmethod
    def find_product_id_by_name(
        list_body: ProductListResponse,
        name: str,
    ) -> int | None:
        for row in list_body.get("Data", []):
            row_name = row.get("Name") or ""
            if name == row_name or name in row_name:
                product_id = row.get("Id")
                if product_id is not None:
                    return int(product_id)
        return None

    def get_product_id_by_name(self, name: str) -> int | None:
        response = self.list(search_name=name)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        return self.find_product_id_by_name(body, name)
