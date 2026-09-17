"""Stable selectors for admin Category list/create/edit views."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriesSelectors:
    LIST_URL_PATH: str = "/Admin/Category/List"
    CREATE_URL_PATH: str = "/Admin/Category/Create"
    EDIT_URL_PATH: str = "/Admin/Category/Edit"

    NAV_CATEGORIES: str = "a.nav-link[href*='/Admin/Category/List']"

    ADD_NEW_BUTTON: str = "a.btn.btn-primary[href*='/Admin/Category/Create']"
    SEARCH_NAME: str = "#SearchCategoryName"
    SEARCH_BUTTON: str = "#search-categories"
    GRID: str = "#categories-grid"
    GRID_ROWS: str = "#categories-grid tbody tr"
    GRID_ROW_CHECKBOX: str = "input.checkboxGroups[name='checkbox_categories']"
    EDIT_LINK: str = "a[href*='/Admin/Category/Edit/']"

    FORM: str = "#category-form"
    DELETE_BUTTON: str = "#category-delete"
    DELETE_CONFIRM_MODAL: str = "#categorymodel-Delete-delete-confirmation"
    DELETE_CONFIRM_SUBMIT: str = (
        "#categorymodel-Delete-delete-confirmation button[type='submit']"
    )
    BACK_TO_LIST: str = "a:has-text('back to category list')"

    # Distinct from common VALIDATION_SUMMARY (div-prefixed for Category forms)
    VALIDATION_SUMMARY: str = "div.validation-summary-errors"


categories_selectors = CategoriesSelectors()
