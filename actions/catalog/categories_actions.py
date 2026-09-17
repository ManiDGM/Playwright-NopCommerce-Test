"""Business flows for admin Category UI operations."""

from playwright.sync_api import Page

from api.actions.catalog.categories_actions import unique_category_name
from pages.catalog.categories_page import CategoriesPage
from selectors.catalog.categories_selectors import categories_selectors


class CategoriesActions:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.categories_page = CategoriesPage(page, self.base_url)

    def open_category_list(self) -> None:
        self.categories_page.navigate_to_list()

    def create_category(self, name: str) -> None:
        self.categories_page.click_add_new()
        self.categories_page.fill_name(name)
        self.categories_page.click_save()

    def create_category_with_empty_name(self) -> None:
        self.categories_page.click_add_new()
        self.categories_page.clear_name()
        self.categories_page.click_save()

    def search_by_name(self, name: str) -> None:
        self.categories_page.fill_search_name(name)
        self.categories_page.click_search()

    def filter_by_published(self, published_option_value: str) -> None:
        """Filter list: 0=all, 1=published only, 2=unpublished only."""
        self.categories_page.select_published_filter(published_option_value)
        self.categories_page.click_search()

    def edit_category_name(self, current_name: str, new_name: str) -> None:
        self.search_by_name(current_name)
        self.categories_page.open_edit_for_name(current_name)
        self.categories_page.fill_name(new_name)
        self.categories_page.click_save()

    def delete_category_from_edit(self, name: str) -> None:
        self.search_by_name(name)
        self.categories_page.open_edit_for_name(name)
        self.categories_page.click_delete_on_edit()
        self.categories_page.confirm_delete_on_edit()

    def delete_selected_categories(self, *, search_term: str, names: list[str]) -> None:
        self.search_by_name(search_term)
        for name in names:
            self.categories_page.select_row_by_name(name)
        self.categories_page.click_delete_selected()
        self.categories_page.confirm_delete_selected()

    def navigate_to_category_list(self) -> None:
        """Teardown helper: return to Category list (goto avoids modal/nav races)."""
        grid = self.page.locator(categories_selectors.GRID)
        if grid.count() and grid.is_visible():
            return
        self.categories_page.navigate_to_list()

    def generate_unique_name(self, prefix: str = "auto") -> str:
        return unique_category_name(prefix)
