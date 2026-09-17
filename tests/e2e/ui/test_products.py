"""UI scenarios for admin Product management."""

from __future__ import annotations

import json
import logging
import re

import pytest
from playwright.sync_api import Page, expect

from actions.catalog.products_actions import ProductsActions
from api.actions.catalog.products_actions import ProductsActions as ApiProductsActions
from selectors.catalog.products_selectors import products_selectors
from selectors.common_selectors import common_selectors

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture
def products_ui(page: Page, base_url: str) -> ProductsActions:
    actions = ProductsActions(page, base_url)
    actions.open_product_list()
    return actions


@pytest.fixture
def api_products(api_request_context) -> ApiProductsActions:
    return ApiProductsActions(api_request_context)


@pytest.fixture(autouse=True)
def _teardown_to_product_list(products_ui: ProductsActions):
    yield
    products_ui.navigate_to_product_list()


class TestProducts:
    @classmethod
    def setup_class(cls) -> None:
        cls._created_names: list[str] = []

    def test_scenario_1_view_product_list(self, products_ui: ProductsActions) -> None:
        log_data("Scenario", {"title": "View the product list"})
        expect(products_ui.page.locator(products_selectors.GRID)).to_be_visible()
        expect(products_ui.page.locator(products_selectors.ADD_NEW_BUTTON)).to_be_visible()
        expect(products_ui.page.locator(products_selectors.GO_TO_SKU_INPUT)).to_be_visible()

    def test_scenario_2_search_products_by_name(
        self,
        products_ui: ProductsActions,
        api_products: ApiProductsActions,
    ) -> None:
        name, create_response = api_products.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()
        self._created_names.append(name)

        products_ui.search_by_name(name)
        log_data("Search term", name)
        expect(products_ui.products_page.row_containing_name(name)).to_be_visible()

    def test_scenario_3_create_product_with_valid_name(
        self,
        products_ui: ProductsActions,
    ) -> None:
        name = products_ui.generate_unique_name()
        log_data("Create payload", {"Name": name})
        products_ui.create_product(name)
        self._created_names.append(name)

        expect(products_ui.page).to_have_url(
            re.compile(r".*/Admin/Product/List(?:\?.*)?$")
        )
        expect(products_ui.products_page.success_alert()).to_be_visible()
        products_ui.search_by_name(name)
        expect(products_ui.products_page.row_containing_name(name)).to_be_visible()

    def test_scenario_4_reject_empty_name_on_create(
        self,
        products_ui: ProductsActions,
    ) -> None:
        log_data("Scenario", {"Name": ""})
        products_ui.create_product_with_empty_name()

        expect(products_ui.page).to_have_url(
            re.compile(r".*/Admin/Product/Create(?:\?.*)?$")
        )
        expect(products_ui.products_page.name_validation_error()).to_be_visible()

    def test_scenario_5_edit_product_name(
        self,
        products_ui: ProductsActions,
        api_products: ApiProductsActions,
    ) -> None:
        original_name, create_response = api_products.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()

        new_name = products_ui.generate_unique_name()
        log_data("Edit names", {"from": original_name, "to": new_name})
        products_ui.edit_product_name(original_name, new_name)
        self._created_names.append(new_name)

        expect(products_ui.page).to_have_url(
            re.compile(r".*/Admin/Product/List(?:\?.*)?$")
        )
        products_ui.search_by_name(new_name)
        expect(products_ui.products_page.row_containing_name(new_name)).to_be_visible()

    def test_scenario_6_delete_single_product_from_edit(
        self,
        products_ui: ProductsActions,
        api_products: ApiProductsActions,
    ) -> None:
        name, create_response = api_products.create_random()
        log_data("API seed create status", create_response.status)
        assert create_response.status in (200, 302), create_response.text()

        log_data("Delete target", {"Name": name})
        products_ui.delete_product_from_edit(name)

        expect(products_ui.page).to_have_url(
            re.compile(r".*/Admin/Product/List(?:\?.*)?$")
        )
        products_ui.search_by_name(name)
        expect(products_ui.products_page.row_containing_name(name)).to_have_count(0)

    def test_scenario_7_delete_selected_products(
        self,
        products_ui: ProductsActions,
        api_products: ApiProductsActions,
    ) -> None:
        search_term = products_ui.generate_unique_name("auto_bulk")
        name_one = f"{search_term}_one"
        name_two = f"{search_term}_two"

        response_one = api_products.create(name_one)
        response_two = api_products.create(name_two)
        log_data("API seed create statuses", {
            "searchTerm": search_term,
            "names": [name_one, name_two],
            "statuses": [response_one.status, response_two.status],
        })
        assert response_one.status in (200, 302), response_one.text()
        assert response_two.status in (200, 302), response_two.text()

        log_data("Delete selected targets", [name_one, name_two])
        products_ui.delete_selected_products(
            search_term=search_term,
            names=[name_one, name_two],
        )

        products_ui.search_by_name(search_term)
        expect(products_ui.products_page.row_containing_name(name_one)).to_have_count(0)
        expect(products_ui.products_page.row_containing_name(name_two)).to_have_count(0)

    def test_scenario_8_go_to_product_by_sku(
        self,
        products_ui: ProductsActions,
        api_products: ApiProductsActions,
    ) -> None:
        name, sku, create_response = api_products.create_random_with_sku()
        log_data("API seed create", {
            "Name": name,
            "Sku": sku,
            "status": create_response.status,
        })
        assert create_response.status in (200, 302), create_response.text()
        self._created_names.append(name)

        product_id = api_products.get_product_id_by_name(name)
        log_data("Go-to-SKU", {"Sku": sku, "productId": product_id})
        assert product_id is not None

        products_ui.go_to_product_by_sku(sku)
        expect(products_ui.page).to_have_url(
            re.compile(rf".*/Admin/Product/Edit/{product_id}(?:\?.*)?$")
        )
        expect(products_ui.page.locator(products_selectors.FORM)).to_be_visible()
        expect(products_ui.page.locator(common_selectors.NAME)).to_have_value(name)
