"""UI interactions for admin Product Review list/edit views."""

from playwright.sync_api import Locator, Page

from selectors.catalog.product_reviews_selectors import product_reviews_selectors
from selectors.common_selectors import common_selectors


class ProductReviewsPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def _expand_catalog_menu_if_needed(self) -> None:
        catalog = self.page.locator(common_selectors.NAV_CATALOG)
        if catalog.count() == 0:
            return
        parent = catalog.first.locator("xpath=ancestor::li[contains(@class,'has-treeview')]")
        if parent.count() and "menu-open" not in (parent.first.get_attribute("class") or ""):
            catalog.first.click()

    def navigate_to_list_via_menu(self) -> None:
        self._expand_catalog_menu_if_needed()
        self.page.locator(product_reviews_selectors.NAV_PRODUCT_REVIEWS).click()
        self.page.locator(product_reviews_selectors.GRID).wait_for(state="visible")

    def fill_search_text(self, text: str) -> None:
        self.page.locator(product_reviews_selectors.SEARCH_TEXT).fill(text)

    def select_approved_filter(self, value: str) -> None:
        self.page.locator(product_reviews_selectors.SEARCH_APPROVED).select_option(value)

    def click_search(self) -> None:
        self.page.locator(product_reviews_selectors.SEARCH_BUTTON).click()

    def grid(self) -> Locator:
        return self.page.locator(product_reviews_selectors.GRID)

    def row_containing_title(self, title: str) -> Locator:
        return self.grid().locator("tbody tr").filter(has_text=title)

    def open_edit_for_title(self, title: str) -> None:
        self.row_containing_title(title).locator("a.btn").first.click()
        self.page.locator(product_reviews_selectors.TITLE).wait_for(state="visible")

    def select_row_by_title(self, title: str) -> None:
        row = self.row_containing_title(title)
        row.locator(product_reviews_selectors.GRID_ROW_CHECKBOX).check()

    def fill_title(self, title: str) -> None:
        self.page.locator(product_reviews_selectors.TITLE).fill(title)

    def clear_title(self) -> None:
        self.page.locator(product_reviews_selectors.TITLE).fill("")

    def fill_review_text(self, review_text: str) -> None:
        self.page.locator(product_reviews_selectors.REVIEW_TEXT).fill(review_text)

    def clear_review_text(self) -> None:
        self.page.locator(product_reviews_selectors.REVIEW_TEXT).fill("")

    def click_save(self) -> None:
        self.page.locator(common_selectors.SAVE_BUTTON).click()

    def click_approve_selected(self) -> None:
        self.page.locator(product_reviews_selectors.APPROVE_SELECTED_BUTTON).click()

    def click_disapprove_selected(self) -> None:
        self.page.locator(product_reviews_selectors.DISAPPROVE_SELECTED_BUTTON).click()

    def click_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_BUTTON).click()

    def confirm_delete_selected(self) -> None:
        self.page.locator(common_selectors.DELETE_SELECTED_CONFIRM).click()

    def click_back_to_list(self) -> None:
        self.page.locator(product_reviews_selectors.BACK_TO_LIST).first.click()
        self.page.locator(product_reviews_selectors.GRID).wait_for(state="visible")

    def title_validation_error(self) -> Locator:
        return self.page.locator(product_reviews_selectors.TITLE_VALIDATION)

    def review_text_validation_error(self) -> Locator:
        return self.page.locator(product_reviews_selectors.REVIEW_TEXT_VALIDATION)

    def validation_summary(self) -> Locator:
        return self.page.locator(common_selectors.VALIDATION_SUMMARY)

    def success_alert(self) -> Locator:
        return self.page.locator(common_selectors.SUCCESS_ALERT)

    def approve_selected_button(self) -> Locator:
        return self.page.locator(product_reviews_selectors.APPROVE_SELECTED_BUTTON)

    def disapprove_selected_button(self) -> Locator:
        return self.page.locator(product_reviews_selectors.DISAPPROVE_SELECTED_BUTTON)

    def delete_selected_button(self) -> Locator:
        return self.page.locator(common_selectors.DELETE_SELECTED_BUTTON)
