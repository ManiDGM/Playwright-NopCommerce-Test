"""URL path constants for admin Product MVC/AJAX endpoints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductsEndpoints:
    LIST_PAGE: str = "/Admin/Product/List"
    PRODUCT_LIST: str = "/Admin/Product/ProductList"
    CREATE_PAGE: str = "/Admin/Product/Create"
    CREATE: str = "/Admin/Product/Create"
    EDIT_PAGE: str = "/Admin/Product/Edit/{product_id}"
    EDIT: str = "/Admin/Product/Edit"
    DELETE: str = "/Admin/Product/Delete/{product_id}"
    DELETE_SELECTED: str = "/Admin/Product/DeleteSelected"
    GO_TO_SKU: str = "/Admin/Product/List"

    @staticmethod
    def edit_page(product_id: int) -> str:
        return f"/Admin/Product/Edit/{product_id}"

    @staticmethod
    def delete(product_id: int) -> str:
        return f"/Admin/Product/Delete/{product_id}"


PRODUCTS_ENDPOINTS = ProductsEndpoints()
