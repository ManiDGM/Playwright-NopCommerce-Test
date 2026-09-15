"""Request/response payload types for admin Category endpoints."""

from __future__ import annotations

from typing import Any, TypedDict


CategoryScalar = str | int | bool


class CategoryListSearchPayload(TypedDict, total=False):
    draw: str
    start: str
    length: str
    SearchCategoryName: str
    SearchPublishedId: str
    SearchStoreId: str


class CategoryCreatePayload(TypedDict, total=False):
    Name: str
    PageSize: CategoryScalar
    AllowCustomersToSelectPageSize: CategoryScalar
    Published: CategoryScalar
    DisplayOrder: CategoryScalar
    ParentCategoryId: CategoryScalar
    CategoryTemplateId: CategoryScalar
    ShowOnHomepage: CategoryScalar
    PriceRangeFiltering: CategoryScalar
    ManuallyPriceRange: CategoryScalar


class CategoryEditPayload(CategoryCreatePayload, total=False):
    Id: CategoryScalar


class CategoryModelResponse(TypedDict, total=False):
    Id: int
    Name: str
    Breadcrumb: str
    Published: bool
    DisplayOrder: int


class CategoryListResponse(TypedDict, total=False):
    draw: int
    recordsTotal: int
    recordsFiltered: int
    Data: list[CategoryModelResponse]


class CategoryDeleteSelectedResponse(TypedDict, total=False):
    Result: bool


CategoryPayload = dict[str, Any]
