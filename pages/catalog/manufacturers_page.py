"""UI interactions for admin Manufacturer list/create/edit views."""

from playwright.sync_api import Locator, Page, expect

from selectors.catalog.manufacturers_selectors import manufacturers_selectors
from selectors.common_selectors import common_selectors


class ManufacturersPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate_to_list(self) -> None:
        """Open Manufacturer list via direct URL (avoids flaky Catalog sidebar expand)."""
        self.page.goto(f"{self.base_url}{manufacturers_selectors.LIST_URL_PATH}")
        self.wait_for_grid()

    def wait_for_grid(self) -> None:
        expect(self.page.locator(manufacturers_selectors.GRID)).to_be_visible()

    def click_add_new(self) -> None:
        self.page.locator(manufacturers_selectors.ADD_NEW_BUTTON).click()
        self.page.locator(manufacturers_selectors.FORM).wait_for(state="visible")

    def fill_name(self, name: str) -> None:
        self.page.locator(common_selectors.NAME).fill(name)

    def clear_name(self) -> None:
        self.page.locator(common_selectors.NAME).fill("")

    def click_save(self) -> None:
        self.page.locator(common_selectors.SAVE_BUTTON).click()

    def fill_search_name(self, name: str) -> None:
        self.page.locator(manufacturers_selectors.SEARCH_NAME).fill(name)

    def select_published_filter(self, value: str) -> None:
        self.page.locator(common_selectors.SEARCH_PUBLISHED).select_option(value)

    def click_search(self) -> None:
        self.page.locator(manufacturers_selectors.SEARCH_BUTTON).click()

    def grid(self) -> Locator:
        return self.page.locator(manufacturers_selectors.GRID)

    def row_containing_name(self, name: str) -> Locator:
        return self.grid().locator("tbody tr").filter(has_text=name)

    def open_edit_for_name(self, name: str) -> None:
        self.row_containing_name(name).locator("a").first.click()
        self.page.locator(manufacturers_selectors.FORM).wait_for(state="visible")

    def select_row_by_name(self, name: str) -> None:
        row = self.row_containing_name(name)
        row.locator(manufacturers_selectors.GRID_ROW_CHECKBOX).check()

    def click_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_BUTTON).click()

    def confirm_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_CONFIRM).click()

    def click_delete_on_edit(self) -> None:
        self.page.locator(manufacturers_selectors.DELETE_BUTTON).click()
        expect(self.page.locator(manufacturers_selectors.DELETE_CONFIRM_MODAL)).to_be_visible()

    def confirm_delete_on_edit(self) -> None:
        self.page.locator(manufacturers_selectors.DELETE_CONFIRM_SUBMIT).click()

    def click_back_to_list(self) -> None:
        self.page.locator(manufacturers_selectors.BACK_TO_LIST).first.click()
        self.wait_for_grid()

    def name_validation_error(self) -> Locator:
        return self.page.locator(common_selectors.NAME_VALIDATION)

    def validation_summary(self) -> Locator:
        return self.page.locator(common_selectors.VALIDATION_SUMMARY)

    def success_alert(self) -> Locator:
        return self.page.locator(common_selectors.SUCCESS_ALERT)
