"""Request/response payload types for admin Product endpoints."""

from __future__ import annotations

from typing import Any, TypedDict


class ProductListSearchPayload(TypedDict, total=False):
    draw: str
    start: int
    length: int
    SearchProductName: str
    SearchCategoryId: int
    SearchIncludeSubCategories: bool
    SearchManufacturerId: int
    SearchStoreId: int
    SearchWarehouseId: int
    SearchVendorId: int
    SearchProductTypeId: int
    SearchPublishedId: int


class ProductCreatePayload(TypedDict, total=False):
    Name: str
    Sku: str
    ProductTypeId: int
    ProductTemplateId: int
    VisibleIndividually: bool
    Published: bool
    AllowCustomerReviews: bool
    IsShipEnabled: bool
    StockQuantity: int
    OrderMinimumQuantity: int
    OrderMaximumQuantity: int
    NotifyAdminForQuantityBelow: int
    MaxNumberOfDownloads: int
    UnlimitedDownloads: bool
    RecurringCycleLength: int
    RecurringTotalCycles: int
    RentalPriceLength: int
    MaximumCustomerEnteredPrice: int
    ManageInventoryMethodId: int
    VendorId: int
    TaxCategoryId: int


class ProductEditPayload(ProductCreatePayload, total=False):
    Id: int
    LastStockQuantity: int


class ProductModelResponse(TypedDict, total=False):
    Id: int
    Name: str
    Sku: str
    Published: bool
    ProductTypeId: int
    FormattedPrice: str
    StockQuantityStr: str


class ProductListResponse(TypedDict, total=False):
    draw: str
    recordsTotal: int
    recordsFiltered: int
    Data: list[ProductModelResponse]


class ProductDeleteSelectedResponse(TypedDict, total=False):
    Result: bool


ProductPayload = dict[str, Any]
