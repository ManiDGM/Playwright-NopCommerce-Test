"""Business flows for admin Product Review UI operations."""

from playwright.sync_api import Page

from api.actions.catalog.product_reviews_actions import (
    unique_review_text,
    unique_review_title,
)
from pages.catalog.product_reviews_page import ProductReviewsPage
from selectors.catalog.product_reviews_selectors import product_reviews_selectors


class ProductReviewsActions:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.product_reviews_page = ProductReviewsPage(page, self.base_url)

    def open_product_review_list(self) -> None:
        self.product_reviews_page.goto_list()

    def search_by_text(self, text: str) -> None:
        self.product_reviews_page.fill_search_text(text)
        self.product_reviews_page.click_search()
        self.product_reviews_page.wait_for_grid()

    def filter_by_approved(self, approved_option_value: str) -> None:
        """Filter list: 0=all, 1=approved only, 2=disapproved only."""
        self.product_reviews_page.select_approved_filter(approved_option_value)
        self.product_reviews_page.click_search()
        self.product_reviews_page.wait_for_grid()

    def edit_title_and_review_text(
        self,
        current_title: str,
        new_title: str,
        new_review_text: str,
    ) -> None:
        self.search_by_text(current_title)
        self.product_reviews_page.open_edit_for_title(current_title)
        self.product_reviews_page.fill_title(new_title)
        self.product_reviews_page.fill_review_text(new_review_text)
        self.product_reviews_page.click_save()

    def open_edit_and_clear_title(self, title: str) -> None:
        self.search_by_text(title)
        self.product_reviews_page.open_edit_for_title(title)
        self.product_reviews_page.clear_title()
        self.product_reviews_page.click_save()

    def open_edit_and_clear_review_text(self, title: str) -> None:
        self.search_by_text(title)
        self.product_reviews_page.open_edit_for_title(title)
        self.product_reviews_page.clear_review_text()
        self.product_reviews_page.click_save()

    def approve_selected_by_title(self, title: str) -> None:
        self.search_by_text(title)
        self.product_reviews_page.select_row_by_title(title)
        with self.page.expect_response(
            lambda response: "/Admin/ProductReview/ApproveSelected" in response.url
            and response.request.method == "POST",
        ):
            self.product_reviews_page.click_approve_selected()
        self.product_reviews_page.wait_for_grid()

    def disapprove_selected_by_title(self, title: str) -> None:
        self.search_by_text(title)
        self.product_reviews_page.select_row_by_title(title)
        with self.page.expect_response(
            lambda response: "/Admin/ProductReview/DisapproveSelected" in response.url
            and response.request.method == "POST",
        ):
            self.product_reviews_page.click_disapprove_selected()
        self.product_reviews_page.wait_for_grid()

    def delete_selected_by_title(self, title: str) -> None:
        self.search_by_text(title)
        self.product_reviews_page.select_row_by_title(title)
        self.product_reviews_page.click_delete_selected()
        with self.page.expect_response(
            lambda response: "/Admin/ProductReview/DeleteSelected" in response.url
            and response.request.method == "POST",
        ):
            self.product_reviews_page.confirm_delete_selected()
        self.product_reviews_page.wait_for_grid()

    def navigate_to_product_review_list(self) -> None:
        """Teardown helper: return to Product reviews list via navigation."""
        grid = self.page.locator(product_reviews_selectors.GRID)
        if grid.count() and grid.is_visible():
            return
        title = self.page.locator(product_reviews_selectors.TITLE)
        if title.count() and title.is_visible():
            self.product_reviews_page.click_back_to_list()
            return
        self.open_product_review_list()

    def generate_unique_title(self, prefix: str = "auto_review") -> str:
        return unique_review_title(prefix)

    def generate_unique_review_text(self, prefix: str = "auto_review_text") -> str:
        return unique_review_text(prefix)
