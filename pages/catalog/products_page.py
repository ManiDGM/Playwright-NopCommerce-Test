"""UI interactions for admin Product list/create/edit views."""

from playwright.sync_api import Locator, Page

from selectors.catalog.products_selectors import products_selectors
from selectors.common_selectors import common_selectors


class ProductsPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def _expand_catalog_menu_if_needed(self) -> None:
        catalog = self.page.locator(common_selectors.NAV_CATALOG)
        if catalog.count() == 0:
            return
        parent = catalog.first.locator(
            "xpath=ancestor::li[contains(@class,'has-treeview')]"
        )
        if parent.count() and "menu-open" not in (parent.first.get_attribute("class") or ""):
            catalog.first.click()

    def navigate_to_list_via_menu(self) -> None:
        self._expand_catalog_menu_if_needed()
        self.page.locator(products_selectors.NAV_PRODUCTS).click()
        self.page.locator(products_selectors.GRID).wait_for(state="visible")

    def click_add_new(self) -> None:
        self.page.locator(products_selectors.ADD_NEW_BUTTON).click()
        self.page.locator(products_selectors.FORM).wait_for(state="visible")

    def fill_name(self, name: str) -> None:
        self.page.locator(common_selectors.NAME).fill(name)

    def clear_name(self) -> None:
        self.page.locator(common_selectors.NAME).fill("")

    def fill_sku(self, sku: str) -> None:
        self.page.locator(products_selectors.SKU).fill(sku)

    def click_save(self) -> None:
        self.page.locator(common_selectors.SAVE_BUTTON).click()

    def fill_search_name(self, name: str) -> None:
        self.page.locator(products_selectors.SEARCH_NAME).fill(name)

    def click_search(self) -> None:
        self.page.locator(products_selectors.SEARCH_BUTTON).click()

    def fill_go_to_sku(self, sku: str) -> None:
        self.page.locator(products_selectors.GO_TO_SKU_INPUT).fill(sku)

    def click_go_to_sku(self) -> None:
        self.page.locator(products_selectors.GO_TO_SKU_BUTTON).click()

    def grid(self) -> Locator:
        return self.page.locator(products_selectors.GRID)

    def row_containing_name(self, name: str) -> Locator:
        return self.grid().locator("tbody tr").filter(has_text=name)

    def open_edit_for_name(self, name: str) -> None:
        self.row_containing_name(name).locator(products_selectors.EDIT_LINK).click()
        self.page.locator(products_selectors.FORM).wait_for(state="visible")

    def select_row_by_name(self, name: str) -> None:
        row = self.row_containing_name(name)
        row.locator(products_selectors.GRID_ROW_CHECKBOX).check()

    def click_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_BUTTON).click()

    def confirm_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_CONFIRM).click()

    def click_delete_on_edit(self) -> None:
        self.page.locator(products_selectors.DELETE_BUTTON).click()

    def confirm_delete_on_edit(self) -> None:
        self.page.locator(products_selectors.DELETE_CONFIRM_SUBMIT).click()

    def click_back_to_list(self) -> None:
        self.page.locator(products_selectors.BACK_TO_LIST).first.click()
        self.page.locator(products_selectors.GRID).wait_for(state="visible")

    def name_validation_error(self) -> Locator:
        return self.page.locator(common_selectors.NAME_VALIDATION)

    def validation_summary(self) -> Locator:
        return self.page.locator(common_selectors.VALIDATION_SUMMARY)

    def success_alert(self) -> Locator:
        return self.page.locator(common_selectors.SUCCESS_ALERT)
