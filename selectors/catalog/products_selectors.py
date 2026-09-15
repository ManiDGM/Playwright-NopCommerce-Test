"""Stable selectors for admin Product list/create/edit views."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductsSelectors:
    LIST_URL_PATH: str = "/Admin/Product/List"
    CREATE_URL_PATH: str = "/Admin/Product/Create"

    NAV_PRODUCTS: str = "a.nav-link[href*='/Admin/Product/List']"

    ADD_NEW_BUTTON: str = "a[href*='/Admin/Product/Create']"
    SEARCH_NAME: str = "#SearchProductName"
    SEARCH_BUTTON: str = "#search-products"
    GRID: str = "#products-grid"

    GO_TO_SKU_INPUT: str = "#GoDirectlyToSku"
    GO_TO_SKU_BUTTON: str = "#go-to-product-by-sku"

    FORM: str = "#product-form"
    SKU: str = "#Sku"
    DELETE_BUTTON: str = "#product-delete"
    DELETE_CONFIRM_SUBMIT: str = (
        "#productmodel-Delete-delete-confirmation button[type='submit']"
    )
    BACK_TO_LIST: str = "a[href*='/Admin/Product/List']"
    EDIT_LINK: str = "a[href*='/Admin/Product/Edit']"
    GRID_ROW_CHECKBOX: str = "input[name='checkbox_products']"


products_selectors = ProductsSelectors()
