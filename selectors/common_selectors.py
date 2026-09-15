"""Shared selector values used by 2+ features."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommonSelectors:
    NAV_CATALOG: str = "a.nav-link:has(p:text-is('Catalog'))"
    DELETE_SELECTED_BUTTON: str = "#delete-selected"
    DELETE_SELECTED_CONFIRM: str = (
        "#delete-selected-action-confirmation-submit-button"
    )
    NAME: str = "#Name"
    PUBLISHED: str = "#Published"
    SEARCH_PUBLISHED: str = "#SearchPublishedId"
    SAVE_BUTTON: str = "button[name='save']"
    NAME_VALIDATION: str = "span.field-validation-error[data-valmsg-for='Name']"
    VALIDATION_SUMMARY: str = ".validation-summary-errors"
    SUCCESS_ALERT: str = ".alert-success, .alert.alert-success"


common_selectors = CommonSelectors()
