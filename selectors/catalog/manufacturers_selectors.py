"""Stable selectors for admin Manufacturer list/create/edit views."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ManufacturersSelectors:
    LIST_URL_PATH: str = "/Admin/Manufacturer/List"
    CREATE_URL_PATH: str = "/Admin/Manufacturer/Create"

    NAV_MANUFACTURERS: str = "a.nav-link[href*='/Admin/Manufacturer/List']"

    ADD_NEW_BUTTON: str = "a.btn.btn-primary[href*='/Admin/Manufacturer/Create']"
    SEARCH_NAME: str = "#SearchManufacturerName"
    SEARCH_BUTTON: str = "#search-manufacturers"
    GRID: str = "#manufacturers-grid"
    GRID_ROW_CHECKBOX: str = "input.checkboxGroups[name='checkbox_manufacturers']"
    EDIT_LINK: str = "a[href*='/Admin/Manufacturer/Edit/']"

    FORM: str = "#manufacturer-form"
    DELETE_BUTTON: str = "#manufacturer-delete"
    DELETE_CONFIRM_MODAL: str = "#manufacturermodel-Delete-delete-confirmation"
    DELETE_CONFIRM_SUBMIT: str = (
        "#manufacturermodel-Delete-delete-confirmation button[type='submit']"
    )
    BACK_TO_LIST: str = "a:has-text('back to manufacturer list')"


manufacturers_selectors = ManufacturersSelectors()
