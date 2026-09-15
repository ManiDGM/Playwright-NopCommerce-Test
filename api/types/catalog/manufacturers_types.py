"""Request/response payload types for admin Manufacturer endpoints."""

from __future__ import annotations

from typing import Any, TypedDict


class ManufacturerListSearchPayload(TypedDict, total=False):
    draw: str
    start: int
    length: int
    SearchManufacturerName: str
    SearchPublishedId: int
    SearchStoreId: int


class ManufacturerCreatePayload(TypedDict, total=False):
    Name: str
    PageSize: int
    AllowCustomersToSelectPageSize: bool
    Published: bool
    DisplayOrder: int
    ManufacturerTemplateId: int
    PriceRangeFiltering: bool
    ManuallyPriceRange: bool


class ManufacturerEditPayload(ManufacturerCreatePayload, total=False):
    Id: int


class ManufacturerModelResponse(TypedDict, total=False):
    Id: int
    Name: str
    Published: bool
    DisplayOrder: int


class ManufacturerListResponse(TypedDict, total=False):
    draw: str
    recordsTotal: int
    recordsFiltered: int
    Data: list[ManufacturerModelResponse]


class ManufacturerDeleteSelectedResponse(TypedDict, total=False):
    Result: bool


ManufacturerPayload = dict[str, Any]
