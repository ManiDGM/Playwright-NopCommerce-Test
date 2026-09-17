"""API scenarios for admin Manufacturer MVC/AJAX endpoints."""

from __future__ import annotations

import json
import logging

import pytest
from playwright.sync_api import APIRequestContext

from api.actions.catalog.manufacturers_actions import (
    ManufacturersActions,
    unique_manufacturer_name,
)
from api.endpoints.catalog.manufacturers_endpoints import MANUFACTURERS_ENDPOINTS

logger = logging.getLogger(__name__)


def log_data(label: str, data: object) -> None:
    logger.info("%s:\n%s", label, json.dumps(data, indent=2, default=str))


@pytest.fixture
def manufacturers_api(api_request_context: APIRequestContext) -> ManufacturersActions:
    return ManufacturersActions(api_request_context)


class TestManufacturersApi:
    def test_scenario_1_list_manufacturers_returns_grid_data(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        response = manufacturers_api.list()
        body = manufacturers_api.parse_list_response(response)
        log_data("List response status", response.status)
        log_data("List response body", body)

        assert response.ok
        assert "Data" in body
        assert "recordsTotal" in body

    def test_scenario_2_search_manufacturers_by_name(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        name, create_response = manufacturers_api.create_random()
        log_data(
            "Seeded manufacturer",
            {"Name": name, "createStatus": create_response.status},
        )
        assert create_response.status in (200, 302), create_response.text()

        search_response = manufacturers_api.list(search_name=name)
        search_body = manufacturers_api.parse_list_response(search_response)
        log_data("Search response status", search_response.status)
        log_data("Search response body", search_body)

        assert search_response.ok
        assert manufacturers_api.find_manufacturer_id_by_name(search_body, name) is not None

    def test_scenario_3_create_manufacturer_with_valid_name(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        name = unique_manufacturer_name()
        payload = {**manufacturers_api.DEFAULT_CREATE_FIELDS, "Name": name}
        log_data("Create request payload", payload)

        response = manufacturers_api.create(name)
        log_data("Create response status", response.status)
        log_data("Create response url", response.url)

        assert response.status in (200, 302)
        assert "/Admin/Manufacturer/List" in response.url

        list_response = manufacturers_api.list(search_name=name)
        list_body = manufacturers_api.parse_list_response(list_response)
        log_data("Post-create list body", list_body)
        assert manufacturers_api.find_manufacturer_id_by_name(list_body, name) is not None

    def test_scenario_4_reject_empty_name_on_create(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        payload = {**manufacturers_api.DEFAULT_CREATE_FIELDS, "Name": ""}
        log_data("Create request payload", payload)

        response = manufacturers_api.create("")
        response_text = response.text()
        log_data("Create response status", response.status)
        log_data("Create response url", response.url)
        log_data(
            "Create response validation markers",
            {
                "has_name_valmsg": 'data-valmsg-for="Name"' in response_text,
                "has_field_validation_error": "field-validation-error" in response_text,
                "has_validation_summary": "validation-summary-errors" in response_text,
            },
        )

        # Empty Name fails FluentValidation; nopCommerce redisplays the form (200 HTML).
        assert response.status == 200
        assert 'data-valmsg-for="Name"' in response_text
        assert "field-validation-error" in response_text

    def test_scenario_5_edit_manufacturer_name(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        original_name, create_response = manufacturers_api.create_random()
        assert create_response.status in (200, 302), create_response.text()

        list_response = manufacturers_api.list(search_name=original_name)
        list_body = manufacturers_api.parse_list_response(list_response)
        manufacturer_id = manufacturers_api.find_manufacturer_id_by_name(list_body, original_name)
        assert manufacturer_id is not None

        new_name = unique_manufacturer_name()
        edit_payload = {
            **manufacturers_api.DEFAULT_CREATE_FIELDS,
            "Id": str(manufacturer_id),
            "Name": new_name,
        }
        log_data("Edit request payload", edit_payload)

        edit_response = manufacturers_api.edit(manufacturer_id, new_name)
        log_data("Edit response status", edit_response.status)
        log_data("Edit response url", edit_response.url)

        assert edit_response.status in (200, 302)
        assert "/Admin/Manufacturer/List" in edit_response.url

        updated_list = manufacturers_api.parse_list_response(
            manufacturers_api.list(search_name=new_name),
        )
        log_data("Post-edit list body", updated_list)
        assert manufacturers_api.find_manufacturer_id_by_name(updated_list, new_name) == manufacturer_id

    def test_scenario_6_delete_single_manufacturer(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        name, create_response = manufacturers_api.create_random()
        assert create_response.status in (200, 302), create_response.text()

        list_body = manufacturers_api.parse_list_response(manufacturers_api.list(search_name=name))
        manufacturer_id = manufacturers_api.find_manufacturer_id_by_name(list_body, name)
        assert manufacturer_id is not None
        log_data("Delete target", {"Id": manufacturer_id, "Name": name})

        delete_response = manufacturers_api.delete(manufacturer_id)
        log_data("Delete response status", delete_response.status)
        log_data("Delete response url", delete_response.url)

        assert delete_response.status in (200, 302)
        assert "/Admin/Manufacturer/List" in delete_response.url

        remaining = manufacturers_api.parse_list_response(manufacturers_api.list(search_name=name))
        log_data("Post-delete list body", remaining)
        assert manufacturers_api.find_manufacturer_id_by_name(remaining, name) is None

    def test_scenario_7_delete_selected_manufacturers(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        shared_prefix = unique_manufacturer_name("auto_bulk")
        name_one = f"{shared_prefix}_one"
        name_two = f"{shared_prefix}_two"

        response_one = manufacturers_api.create(name_one)
        response_two = manufacturers_api.create(name_two)
        log_data(
            "Seeded manufacturers",
            {
                "names": [name_one, name_two],
                "statuses": [response_one.status, response_two.status],
            },
        )
        assert response_one.status in (200, 302), response_one.text()
        assert response_two.status in (200, 302), response_two.text()

        list_one = manufacturers_api.parse_list_response(manufacturers_api.list(search_name=name_one))
        list_two = manufacturers_api.parse_list_response(manufacturers_api.list(search_name=name_two))
        manufacturer_id_one = manufacturers_api.find_manufacturer_id_by_name(list_one, name_one)
        manufacturer_id_two = manufacturers_api.find_manufacturer_id_by_name(list_two, name_two)
        assert manufacturer_id_one is not None
        assert manufacturer_id_two is not None

        selected_ids = [manufacturer_id_one, manufacturer_id_two]
        log_data("DeleteSelected request ids", selected_ids)

        delete_response = manufacturers_api.delete_selected(selected_ids)
        response_text = delete_response.text()
        log_data("DeleteSelected response status", delete_response.status)
        log_data("DeleteSelected response body", response_text)

        # Controller returns Json({ Result = true }) on success, or 204 NoContent
        # when selectedIds did not bind. Prefer JSON when present; always verify list.
        delete_body: dict | None = None
        if response_text.strip():
            try:
                delete_body = delete_response.json()
            except ValueError:
                delete_body = None
        log_data("DeleteSelected parsed body", delete_body)

        assert delete_response.status != 204, "selectedIds did not bind (NoContent)"
        assert delete_response.ok
        if delete_body is not None:
            assert delete_body.get("Result") is True

        for name in (name_one, name_two):
            remaining = manufacturers_api.parse_list_response(manufacturers_api.list(search_name=name))
            log_data("Post-delete-selected list body", {"name": name, "body": remaining})
            assert manufacturers_api.find_manufacturer_id_by_name(remaining, name) is None

    def test_scenario_8_filter_manufacturers_by_published_status(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        name, create_response = manufacturers_api.create_random(published=True)
        log_data(
            "Seeded published manufacturer",
            {"Name": name, "createStatus": create_response.status},
        )
        assert create_response.status in (200, 302), create_response.text()

        published_response = manufacturers_api.list(search_name=name, search_published_id=1)
        published_body = manufacturers_api.parse_list_response(published_response)
        log_data("Published filter response status", published_response.status)
        log_data("Published filter response body", published_body)
        assert published_response.ok
        assert manufacturers_api.find_manufacturer_id_by_name(published_body, name) is not None

        unpublished_response = manufacturers_api.list(search_name=name, search_published_id=2)
        unpublished_body = manufacturers_api.parse_list_response(unpublished_response)
        log_data("Unpublished filter response status", unpublished_response.status)
        log_data("Unpublished filter response body", unpublished_body)
        assert unpublished_response.ok
        assert manufacturers_api.find_manufacturer_id_by_name(unpublished_body, name) is None

    def test_list_page_is_reachable(
        self,
        manufacturers_api: ManufacturersActions,
    ) -> None:
        response = manufacturers_api.client.get_list_page()
        log_data("List page status", response.status)
        assert response.ok
        assert MANUFACTURERS_ENDPOINTS.LIST_PAGE in response.url
