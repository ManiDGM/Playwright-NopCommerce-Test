"""Business flows for admin Manufacturer UI operations."""

from playwright.sync_api import Page

from api.actions.catalog.manufacturers_actions import unique_manufacturer_name
from pages.catalog.manufacturers_page import ManufacturersPage


class ManufacturersActions:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.manufacturers_page = ManufacturersPage(page, self.base_url)

    def open_manufacturer_list(self) -> None:
        self.manufacturers_page.navigate_to_list_via_menu()

    def create_manufacturer(self, name: str) -> None:
        self.manufacturers_page.click_add_new()
        self.manufacturers_page.fill_name(name)
        self.manufacturers_page.click_save()

    def create_manufacturer_with_empty_name(self) -> None:
        self.manufacturers_page.click_add_new()
        self.manufacturers_page.clear_name()
        self.manufacturers_page.click_save()

    def search_by_name(self, name: str) -> None:
        self.manufacturers_page.fill_search_name(name)
        self.manufacturers_page.click_search()

    def filter_by_published(self, published_option_value: str) -> None:
        """Filter list: 0=all, 1=published only, 2=unpublished only."""
        self.manufacturers_page.select_published_filter(published_option_value)
        self.manufacturers_page.click_search()

    def edit_manufacturer_name(self, current_name: str, new_name: str) -> None:
        self.search_by_name(current_name)
        self.manufacturers_page.open_edit_for_name(current_name)
        self.manufacturers_page.fill_name(new_name)
        self.manufacturers_page.click_save()

    def delete_manufacturer_from_edit(self, name: str) -> None:
        self.search_by_name(name)
        self.manufacturers_page.open_edit_for_name(name)
        self.manufacturers_page.click_delete_on_edit()
        self.manufacturers_page.confirm_delete_on_edit()

    def delete_selected_manufacturers(self, names: list[str]) -> None:
        for name in names:
            self.search_by_name(name)
            self.manufacturers_page.select_row_by_name(name)
        self.manufacturers_page.click_delete_selected()
        self.manufacturers_page.confirm_delete_selected()

    def navigate_to_manufacturer_list(self) -> None:
        """Teardown helper: return to Manufacturer list via navigation."""
        from selectors.catalog.manufacturers_selectors import manufacturers_selectors

        if self.page.locator(manufacturers_selectors.GRID).is_visible():
            return
        if self.page.locator(manufacturers_selectors.FORM).is_visible():
            self.manufacturers_page.click_back_to_list()
            return
        self.manufacturers_page.navigate_to_list_via_menu()

    def generate_unique_name(self, prefix: str = "auto") -> str:
        return unique_manufacturer_name(prefix)
