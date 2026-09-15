"""UI scenarios for admin Category management."""

from __future__ import annotations

import json
import logging
import re

import pytest
from playwright.sync_api import Page, expect

from actions.catalog.categories_actions import CategoriesActions
from api.actions.catalog.categories_actions import CategoriesActions as ApiCategoriesActions
from selectors.catalog.categories_selectors import categories_selectors

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture
def categories_ui(page: Page, base_url: str) -> CategoriesActions:
    actions = CategoriesActions(page, base_url)
    actions.open_category_list()
    return actions


@pytest.fixture
def api_categories(api_request_context) -> ApiCategoriesActions:
    return ApiCategoriesActions(api_request_context)


@pytest.fixture(autouse=True)
def _teardown_to_category_list(categories_ui: CategoriesActions):
    yield
    categories_ui.navigate_to_category_list()


class TestCategories:
    def test_scenario_1_view_category_list(self, categories_ui: CategoriesActions) -> None:
        log_data("Scenario", {"title": "Scenario 1: View the category list"})
        expect(categories_ui.page.locator(categories_selectors.GRID)).to_be_visible()
        expect(categories_ui.page.locator(categories_selectors.ADD_NEW_BUTTON)).to_be_visible()

    def test_scenario_2_search_categories_by_name(
        self,
        categories_ui: CategoriesActions,
        api_categories: ApiCategoriesActions,
    ) -> None:
        name, create_response = api_categories.create_random()
        log_data(
            "API seed create",
            {"Name": name, "status": create_response.status},
        )
        assert create_response.status in (200, 302), create_response.text()

        categories_ui.search_by_name(name)
        log_data("Search term", {"SearchCategoryName": name})
        expect(categories_ui.categories_page.row_containing_name(name)).to_be_visible()

    def test_scenario_3_create_category_with_valid_name(
        self,
        categories_ui: CategoriesActions,
    ) -> None:
        name = categories_ui.generate_unique_name()
        log_data("Create payload", {"Name": name})
        categories_ui.create_category(name)

        expect(categories_ui.page).to_have_url(
            re.compile(r".*/Admin/Category/List(?:\?.*)?$")
        )
        expect(categories_ui.categories_page.success_alert()).to_be_visible()
        categories_ui.search_by_name(name)
        expect(categories_ui.categories_page.row_containing_name(name)).to_be_visible()

    def test_scenario_4_reject_empty_name_on_create(
        self,
        categories_ui: CategoriesActions,
    ) -> None:
        log_data("Create payload", {"Name": ""})
        categories_ui.create_category_with_empty_name()

        expect(categories_ui.page).to_have_url(
            re.compile(r".*/Admin/Category/Create(?:\?.*)?$")
        )
        expect(categories_ui.categories_page.name_validation_error()).to_be_visible()

    def test_scenario_5_edit_category_name(
        self,
        categories_ui: CategoriesActions,
        api_categories: ApiCategoriesActions,
    ) -> None:
        original_name, create_response = api_categories.create_random()
        assert create_response.status in (200, 302), create_response.text()

        new_name = categories_ui.generate_unique_name()
        log_data("Edit payload", {"from": original_name, "to": new_name})
        categories_ui.edit_category_name(original_name, new_name)

        expect(categories_ui.page).to_have_url(
            re.compile(r".*/Admin/Category/List(?:\?.*)?$")
        )
        categories_ui.search_by_name(new_name)
        expect(categories_ui.categories_page.row_containing_name(new_name)).to_be_visible()

    def test_scenario_6_delete_single_category_from_edit(
        self,
        categories_ui: CategoriesActions,
        api_categories: ApiCategoriesActions,
    ) -> None:
        name, create_response = api_categories.create_random()
        assert create_response.status in (200, 302), create_response.text()

        log_data("Delete target", {"Name": name})
        categories_ui.delete_category_from_edit(name)

        expect(categories_ui.page).to_have_url(
            re.compile(r".*/Admin/Category/List(?:\?.*)?$")
        )
        categories_ui.search_by_name(name)
        expect(categories_ui.categories_page.row_containing_name(name)).to_have_count(0)

    def test_scenario_7_delete_selected_categories(
        self,
        categories_ui: CategoriesActions,
        api_categories: ApiCategoriesActions,
    ) -> None:
        search_term = categories_ui.generate_unique_name("auto_bulk")
        name_one = f"{search_term}_one"
        name_two = f"{search_term}_two"

        response_one = api_categories.create(name_one)
        response_two = api_categories.create(name_two)
        log_data(
            "API seed create",
            {
                "searchTerm": search_term,
                "names": [name_one, name_two],
                "statuses": [response_one.status, response_two.status],
            },
        )
        assert response_one.status in (200, 302), response_one.text()
        assert response_two.status in (200, 302), response_two.text()

        categories_ui.delete_selected_categories(
            search_term=search_term,
            names=[name_one, name_two],
        )

        categories_ui.search_by_name(search_term)
        expect(categories_ui.categories_page.row_containing_name(name_one)).to_have_count(0)
        expect(categories_ui.categories_page.row_containing_name(name_two)).to_have_count(0)

    def test_scenario_8_filter_categories_by_published_status(
        self,
        categories_ui: CategoriesActions,
        api_categories: ApiCategoriesActions,
    ) -> None:
        name, create_response = api_categories.create_random(published=True)
        log_data(
            "API seed create",
            {"Name": name, "Published": True, "status": create_response.status},
        )
        assert create_response.status in (200, 302), create_response.text()

        categories_ui.search_by_name(name)
        log_data("Published filter", {"SearchCategoryName": name, "SearchPublishedId": "1"})
        categories_ui.filter_by_published("1")
        expect(categories_ui.categories_page.row_containing_name(name)).to_be_visible()

        log_data("Unpublished filter", {"SearchCategoryName": name, "SearchPublishedId": "2"})
        categories_ui.filter_by_published("2")
        expect(categories_ui.categories_page.row_containing_name(name)).to_have_count(0)
