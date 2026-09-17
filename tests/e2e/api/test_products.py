"""API scenarios for admin Product MVC/AJAX endpoints."""

from __future__ import annotations

import json
import logging

import pytest
from playwright.sync_api import APIRequestContext

from api.actions.catalog.products_actions import ProductsActions, unique_product_name
from api.endpoints.catalog.products_endpoints import PRODUCTS_ENDPOINTS

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture
def products_api(api_request_context: APIRequestContext) -> ProductsActions:
    return ProductsActions(api_request_context)


class TestProductsApi:
    @classmethod
    def setup_class(cls) -> None:
        cls._created_ids: list[int] = []

    def test_scenario_1_list_products_returns_grid_data(
        self,
        products_api: ProductsActions,
    ) -> None:
        response = products_api.list()
        body = products_api.parse_list_response(response)
        log_data("List response status", response.status)
        log_data("List response body", body)

        assert response.ok
        assert "Data" in body
        assert "recordsTotal" in body

    def test_scenario_2_search_products_by_name(
        self,
        products_api: ProductsActions,
    ) -> None:
        name, create_response = products_api.create_random()
        assert create_response.status in (200, 302), create_response.text()
        log_data("Seeded product", {"Name": name, "createStatus": create_response.status})

        search_response = products_api.list(search_name=name)
        search_body = products_api.parse_list_response(search_response)
        log_data("Search response status", search_response.status)
        log_data("Search response body", search_body)

        assert search_response.ok
        product_id = products_api.find_product_id_by_name(search_body, name)
        assert product_id is not None
        self._created_ids.append(product_id)

    def test_scenario_3_create_product_with_valid_name(
        self,
        products_api: ProductsActions,
    ) -> None:
        name = unique_product_name()
        payload = {**products_api.DEFAULT_CREATE_FIELDS, "Name": name}
        log_data("Create request payload", payload)

        response = products_api.create(name)
        log_data("Create response status", response.status)
        log_data("Create response url", response.url)

        assert response.status in (200, 302)
        assert "/Admin/Product/List" in response.url

        list_response = products_api.list(search_name=name)
        list_body = products_api.parse_list_response(list_response)
        log_data("Post-create list body", list_body)
        product_id = products_api.find_product_id_by_name(list_body, name)
        assert product_id is not None
        self._created_ids.append(product_id)

    def test_scenario_4_reject_empty_name_on_create(
        self,
        products_api: ProductsActions,
    ) -> None:
        payload = {**products_api.DEFAULT_CREATE_FIELDS, "Name": ""}
        log_data("Create request payload", payload)

        response = products_api.create("")
        response_text = response.text()
        log_data("Create response status", response.status)
        log_data("Create response url", response.url)

        assert response.status == 200
        assert "/Admin/Product/Create" in response.url
        assert 'data-valmsg-for="Name"' in response_text
        assert "field-validation-error" in response_text

    def test_scenario_5_edit_product_name(
        self,
        products_api: ProductsActions,
    ) -> None:
        original_name, create_response = products_api.create_random()
        assert create_response.status in (200, 302), create_response.text()

        list_response = products_api.list(search_name=original_name)
        list_body = products_api.parse_list_response(list_response)
        product_id = products_api.find_product_id_by_name(list_body, original_name)
        assert product_id is not None

        new_name = unique_product_name()
        edit_payload = {
            **products_api.DEFAULT_CREATE_FIELDS,
            "Id": str(product_id),
            "Name": new_name,
            "StockQuantity": "10000",
            "LastStockQuantity": "10000",
        }
        log_data("Edit request payload", edit_payload)

        edit_response = products_api.edit(product_id, new_name)
        log_data("Edit response status", edit_response.status)
        log_data("Edit response url", edit_response.url)

        assert edit_response.status in (200, 302)
        assert "/Admin/Product/List" in edit_response.url

        updated_list = products_api.parse_list_response(
            products_api.list(search_name=new_name),
        )
        log_data("Post-edit list body", updated_list)
        assert products_api.find_product_id_by_name(updated_list, new_name) == product_id
        self._created_ids.append(product_id)

    def test_scenario_6_delete_single_product(
        self,
        products_api: ProductsActions,
    ) -> None:
        name, create_response = products_api.create_random()
        assert create_response.status in (200, 302), create_response.text()

        list_body = products_api.parse_list_response(products_api.list(search_name=name))
        product_id = products_api.find_product_id_by_name(list_body, name)
        assert product_id is not None
        log_data("Delete target", {"Id": product_id, "Name": name})

        delete_response = products_api.delete(product_id)
        log_data("Delete response status", delete_response.status)
        log_data("Delete response url", delete_response.url)

        assert delete_response.status in (200, 302)
        assert "/Admin/Product/List" in delete_response.url

        remaining = products_api.parse_list_response(products_api.list(search_name=name))
        log_data("Post-delete list body", remaining)
        assert products_api.find_product_id_by_name(remaining, name) is None

    def test_scenario_7_delete_selected_products(
        self,
        products_api: ProductsActions,
    ) -> None:
        name_one, response_one = products_api.create_random()
        name_two, response_two = products_api.create_random()
        assert response_one.status in (200, 302), response_one.text()
        assert response_two.status in (200, 302), response_two.text()

        list_one = products_api.parse_list_response(products_api.list(search_name=name_one))
        list_two = products_api.parse_list_response(products_api.list(search_name=name_two))
        product_id_one = products_api.find_product_id_by_name(list_one, name_one)
        product_id_two = products_api.find_product_id_by_name(list_two, name_two)
        assert product_id_one is not None
        assert product_id_two is not None

        selected_ids = [product_id_one, product_id_two]
        log_data("DeleteSelected request ids", selected_ids)

        delete_response = products_api.delete_selected(selected_ids)
        delete_body = delete_response.json() if delete_response.ok else delete_response.text()
        log_data("DeleteSelected response status", delete_response.status)
        log_data("DeleteSelected response body", delete_body)

        assert delete_response.ok
        assert delete_body.get("Result") is True

        for name in (name_one, name_two):
            remaining = products_api.parse_list_response(products_api.list(search_name=name))
            assert products_api.find_product_id_by_name(remaining, name) is None

    def test_scenario_8_go_to_product_by_sku(
        self,
        products_api: ProductsActions,
    ) -> None:
        name, sku, create_response = products_api.create_random_with_sku()
        assert create_response.status in (200, 302), create_response.text()
        log_data("Seeded product with SKU", {"Name": name, "Sku": sku})

        product_id = products_api.get_product_id_by_name(name)
        assert product_id is not None
        self._created_ids.append(product_id)

        go_response = products_api.go_to_sku(sku)
        log_data("GoToSku response status", go_response.status)
        log_data("GoToSku response url", go_response.url)

        assert go_response.status in (200, 302)
        assert f"/Admin/Product/Edit/{product_id}" in go_response.url

    def test_list_page_is_reachable(
        self,
        products_api: ProductsActions,
    ) -> None:
        response = products_api.client.get_list_page()
        log_data("List page status", response.status)
        assert response.ok
        assert PRODUCTS_ENDPOINTS.LIST_PAGE in response.url
