"""Business flows for admin Manufacturer API operations."""

from __future__ import annotations

import uuid
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from api.clients.catalog.manufacturers_client import ManufacturersClient
from api.types.catalog.manufacturers_types import ManufacturerListResponse, ManufacturerPayload


def unique_manufacturer_name(prefix: str = "auto") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ManufacturersActions:
    DEFAULT_CREATE_FIELDS: dict[str, Any] = {
        "PageSize": "5",
        "AllowCustomersToSelectPageSize": "false",
        "Published": "true",
        "DisplayOrder": "0",
        "ManufacturerTemplateId": "1",
        "PriceRangeFiltering": "false",
        "ManuallyPriceRange": "false",
    }

    def __init__(self, request: APIRequestContext) -> None:
        self.client = ManufacturersClient(request)

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
        payload: ManufacturerPayload = {
            "draw": draw,
            "start": str(start),
            "length": str(length),
            "SearchManufacturerName": search_name,
            "SearchPublishedId": str(search_published_id),
            "SearchStoreId": str(search_store_id),
        }
        return self.client.list_manufacturers(payload)

    def create(
        self,
        name: str | None = None,
        *,
        published: bool = True,
        extra_fields: ManufacturerPayload | None = None,
    ) -> APIResponse:
        # Preserve empty string so validation scenarios can POST Name=""
        resolved_name = unique_manufacturer_name() if name is None else name
        payload: ManufacturerPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Name": resolved_name,
            "Published": "true" if published else "false",
            **(extra_fields or {}),
        }
        return self.client.create_manufacturer(payload)

    def create_random(self, *, published: bool = True) -> tuple[str, APIResponse]:
        name = unique_manufacturer_name()
        response = self.create(name, published=published)
        return name, response

    def edit(self, manufacturer_id: int, name: str, **fields: Any) -> APIResponse:
        payload: ManufacturerPayload = {
            **self.DEFAULT_CREATE_FIELDS,
            "Id": str(manufacturer_id),
            "Name": name,
            **{key: str(value) for key, value in fields.items()},
        }
        return self.client.edit_manufacturer(payload)

    def delete(self, manufacturer_id: int) -> APIResponse:
        return self.client.delete_manufacturer(manufacturer_id)

    def delete_selected(self, manufacturer_ids: list[int]) -> APIResponse:
        return self.client.delete_selected(manufacturer_ids)

    @staticmethod
    def parse_list_response(response: APIResponse) -> ManufacturerListResponse:
        return response.json()

    @staticmethod
    def find_manufacturer_id_by_name(
        list_body: ManufacturerListResponse,
        name: str,
    ) -> int | None:
        for row in list_body.get("Data", []):
            row_name = row.get("Name") or ""
            if name in row_name:
                manufacturer_id = row.get("Id")
                if manufacturer_id is not None:
                    return int(manufacturer_id)
        return None

    def get_manufacturer_id_by_name(self, name: str) -> int | None:
        response = self.list(search_name=name)
        if not response.ok:
            return None
        body = self.parse_list_response(response)
        return self.find_manufacturer_id_by_name(body, name)
