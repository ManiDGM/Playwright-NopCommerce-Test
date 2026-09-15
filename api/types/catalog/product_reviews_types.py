"""Request/response payload types for admin ProductReview endpoints."""

from __future__ import annotations

from typing import Any, TypedDict


class ProductReviewListSearchPayload(TypedDict, total=False):
    draw: str
    start: int
    length: int
    SearchText: str
    SearchStoreId: int
    SearchProductId: int
    SearchApprovedId: int
    CreatedOnFrom: str
    CreatedOnTo: str


class ProductReviewEditPayload(TypedDict, total=False):
    Id: int
    Title: str
    ReviewText: str
    ReplyText: str
    IsApproved: bool


class ProductReviewModelResponse(TypedDict, total=False):
    Id: int
    ProductId: int
    ProductName: str
    CustomerId: int
    CustomerInfo: str
    Title: str
    ReviewText: str
    ReplyText: str
    Rating: int
    IsApproved: bool
    StoreName: str


class ProductReviewListResponse(TypedDict, total=False):
    draw: str
    recordsTotal: int
    recordsFiltered: int
    Data: list[ProductReviewModelResponse]


class ProductReviewSelectedActionResponse(TypedDict, total=False):
    Result: bool


class StorefrontAddReviewPayload(TypedDict, total=False):
    ProductId: int
    AddProductReview_Title: str
    AddProductReview_ReviewText: str
    AddProductReview_Rating: int


ProductReviewPayload = dict[str, Any]
