"""UI scenarios for admin Manufacturer management."""

from __future__ import annotations

import json
import logging

import pytest
from playwright.sync_api import Page, expect

from actions.catalog.manufacturers_actions import ManufacturersActions
from api.actions.catalog.manufacturers_actions import ManufacturersActions as ApiManufacturersActions
from selectors.catalog.manufacturers_selectors import manufacturers_selectors

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture(scope="module")
def manufacturers_ui(page: Page, base_url: str) -> ManufacturersActions:
    actions = ManufacturersActions(page, base_url)
    actions.open_manufacturer_list()
    return actions


@pytest.fixture(scope="module")
def api_manufacturers(api_request_context) -> ApiManufacturersActions:
    return ApiManufacturersActions(api_request_context)


class TestManufacturers:
    @classmethod
    def setup_class(cls) -> None:
        cls._created_names: list[str] = []

    def teardown_method(self, manufacturers_ui: ManufacturersActions) -> None:
        manufacturers_ui.navigate_to_manufacturer_list()

    def test_scenario_1_view_manufacturer_list(self, manufacturers_ui: ManufacturersActions) -> None:
        log_data("Scenario", {"title": "View the manufacturer list"})
        expect(manufacturers_ui.page.locator(manufacturers_selectors.GRID)).to_be_visible()
        expect(manufacturers_ui.page.locator(manufacturers_selectors.ADD_NEW_BUTTON)).to_be_visible()

    def test_scenario_2_search_manufacturers_by_name(
        self,
        manufacturers_ui: ManufacturersActions,
        api_manufacturers: ApiManufacturersActions,
    ) -> None:
        name, create_response = api_manufacturers.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()
        self._created_names.append(name)

        manufacturers_ui.search_by_name(name)
        log_data("Search term", name)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name)).to_be_visible()

    def test_scenario_3_create_manufacturer_with_valid_name(
        self,
        manufacturers_ui: ManufacturersActions,
    ) -> None:
        name = manufacturers_ui.generate_unique_name()
        log_data("Create payload", {"Name": name})
        manufacturers_ui.create_manufacturer(name)
        self._created_names.append(name)

        expect(manufacturers_ui.page).to_have_url(
            lambda url: "/Admin/Manufacturer/List" in url,
        )
        expect(manufacturers_ui.manufacturers_page.success_alert()).to_be_visible()
        manufacturers_ui.search_by_name(name)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name)).to_be_visible()

    def test_scenario_4_reject_empty_name_on_create(
        self,
        manufacturers_ui: ManufacturersActions,
    ) -> None:
        log_data("Scenario", {"Name": ""})
        manufacturers_ui.create_manufacturer_with_empty_name()

        expect(manufacturers_ui.page).to_have_url(
            lambda url: "/Admin/Manufacturer/Create" in url,
        )
        expect(manufacturers_ui.manufacturers_page.name_validation_error()).to_be_visible()

    def test_scenario_5_edit_manufacturer_name(
        self,
        manufacturers_ui: ManufacturersActions,
        api_manufacturers: ApiManufacturersActions,
    ) -> None:
        original_name, create_response = api_manufacturers.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()

        new_name = manufacturers_ui.generate_unique_name()
        log_data("Edit names", {"from": original_name, "to": new_name})
        manufacturers_ui.edit_manufacturer_name(original_name, new_name)
        self._created_names.append(new_name)

        expect(manufacturers_ui.page).to_have_url(
            lambda url: "/Admin/Manufacturer/List" in url,
        )
        manufacturers_ui.search_by_name(new_name)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(new_name)).to_be_visible()

    def test_scenario_6_delete_single_manufacturer_from_edit(
        self,
        manufacturers_ui: ManufacturersActions,
        api_manufacturers: ApiManufacturersActions,
    ) -> None:
        name, create_response = api_manufacturers.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()

        log_data("Delete target", {"Name": name})
        manufacturers_ui.delete_manufacturer_from_edit(name)

        expect(manufacturers_ui.page).to_have_url(
            lambda url: "/Admin/Manufacturer/List" in url,
        )
        manufacturers_ui.search_by_name(name)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name)).to_have_count(0)

    def test_scenario_7_delete_selected_manufacturers(
        self,
        manufacturers_ui: ManufacturersActions,
        api_manufacturers: ApiManufacturersActions,
    ) -> None:
        name_one, response_one = api_manufacturers.create_random()
        name_two, response_two = api_manufacturers.create_random()
        log_data("API seed create statuses", {
            "first": response_one.status,
            "second": response_two.status,
        })
        assert response_one.status in (200, 302), response_one.text()
        assert response_two.status in (200, 302), response_two.text()

        log_data("Delete selected targets", [name_one, name_two])
        manufacturers_ui.delete_selected_manufacturers([name_one, name_two])

        manufacturers_ui.search_by_name(name_one)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name_one)).to_have_count(0)
        manufacturers_ui.search_by_name(name_two)
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name_two)).to_have_count(0)

    def test_scenario_8_filter_manufacturers_by_published_status(
        self,
        manufacturers_ui: ManufacturersActions,
        api_manufacturers: ApiManufacturersActions,
    ) -> None:
        name, create_response = api_manufacturers.create_random(published=True)
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()
        self._created_names.append(name)

        manufacturers_ui.search_by_name(name)
        log_data("Published filter", {"SearchPublishedId": "1"})
        manufacturers_ui.filter_by_published("1")
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name)).to_be_visible()

        log_data("Unpublished filter", {"SearchPublishedId": "2"})
        manufacturers_ui.filter_by_published("2")
        expect(manufacturers_ui.manufacturers_page.row_containing_name(name)).to_have_count(0)
