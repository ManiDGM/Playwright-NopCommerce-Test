"""Stable selectors for admin Product Review list/edit views."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductReviewsSelectors:
    LIST_URL_PATH: str = "/Admin/ProductReview/List"
    EDIT_URL_PATH: str = "/Admin/ProductReview/Edit"

    NAV_PRODUCT_REVIEWS: str = "a.nav-link[href*='/Admin/ProductReview/List']"

    SEARCH_TEXT: str = "#SearchText"
    SEARCH_APPROVED: str = "#SearchApprovedId"
    SEARCH_BUTTON: str = "#search-productreviews"
    GRID: str = "#productreviews-grid"

    APPROVE_SELECTED_BUTTON: str = "#approve-selected"
    DISAPPROVE_SELECTED_BUTTON: str = "#disapprove-selected"

    FORM: str = "form[action*='/Admin/ProductReview/Edit']"
    TITLE: str = "#Title"
    REVIEW_TEXT: str = "#ReviewText"
    REPLY_TEXT: str = "#ReplyText"
    IS_APPROVED: str = "#IsApproved"
    DELETE_BUTTON: str = "#productreview-delete"
    DELETE_CONFIRM_SUBMIT: str = "#productreviewmodel-delete-confirmation button[type='submit']"
    BACK_TO_LIST: str = "a[href*='/Admin/ProductReview/List']"

    TITLE_VALIDATION: str = "span.field-validation-error[data-valmsg-for='Title']"
    REVIEW_TEXT_VALIDATION: str = "span.field-validation-error[data-valmsg-for='ReviewText']"
    GRID_ROW_CHECKBOX: str = "input[name='checkbox_product_reviews']"
    APPROVED_ICON: str = "i.true-icon, i.fas.fa-check.true-icon"
    DISAPPROVED_ICON: str = "i.false-icon, i.fas.fa-times.false-icon"


product_reviews_selectors = ProductReviewsSelectors()
