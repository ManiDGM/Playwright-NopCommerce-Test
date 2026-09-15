"""Business flows for admin Product UI operations."""

from playwright.sync_api import Page

from api.actions.catalog.products_actions import unique_product_name, unique_product_sku
from pages.catalog.products_page import ProductsPage


class ProductsActions:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.products_page = ProductsPage(page, self.base_url)

    def open_product_list(self) -> None:
        self.products_page.navigate_to_list_via_menu()

    def create_product(self, name: str, sku: str | None = None) -> None:
        self.products_page.click_add_new()
        self.products_page.fill_name(name)
        if sku is not None:
            self.products_page.fill_sku(sku)
        self.products_page.click_save()

    def create_product_with_empty_name(self) -> None:
        self.products_page.click_add_new()
        self.products_page.clear_name()
        self.products_page.click_save()

    def search_by_name(self, name: str) -> None:
        self.products_page.fill_search_name(name)
        self.products_page.click_search()

    def edit_product_name(self, current_name: str, new_name: str) -> None:
        self.search_by_name(current_name)
        self.products_page.open_edit_for_name(current_name)
        self.products_page.fill_name(new_name)
        self.products_page.click_save()

    def delete_product_from_edit(self, name: str) -> None:
        self.search_by_name(name)
        self.products_page.open_edit_for_name(name)
        self.products_page.click_delete_on_edit()
        self.products_page.confirm_delete_on_edit()

    def delete_selected_products(self, names: list[str]) -> None:
        for name in names:
            self.search_by_name(name)
            self.products_page.select_row_by_name(name)
        self.products_page.click_delete_selected()
        self.products_page.confirm_delete_selected()

    def go_to_product_by_sku(self, sku: str) -> None:
        self.products_page.fill_go_to_sku(sku)
        self.products_page.click_go_to_sku()

    def navigate_to_product_list(self) -> None:
        """Teardown helper: return to Product list via navigation."""
        from selectors.catalog.products_selectors import products_selectors

        if self.page.locator(products_selectors.GRID).is_visible():
            return
        if self.page.locator(products_selectors.FORM).is_visible():
            self.products_page.click_back_to_list()
            return
        self.products_page.navigate_to_list_via_menu()

    def generate_unique_name(self, prefix: str = "auto") -> str:
        return unique_product_name(prefix)

    def generate_unique_sku(self, prefix: str = "sku") -> str:
        return unique_product_sku(prefix)
