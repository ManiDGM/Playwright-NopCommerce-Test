"""URL path constants for admin Manufacturer MVC/AJAX endpoints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ManufacturersEndpoints:
    LIST_PAGE: str = "/Admin/Manufacturer/List"
    LIST: str = "/Admin/Manufacturer/List"
    CREATE_PAGE: str = "/Admin/Manufacturer/Create"
    CREATE: str = "/Admin/Manufacturer/Create"
    EDIT_PAGE: str = "/Admin/Manufacturer/Edit/{manufacturer_id}"
    EDIT: str = "/Admin/Manufacturer/Edit"
    DELETE: str = "/Admin/Manufacturer/Delete/{manufacturer_id}"
    DELETE_SELECTED: str = "/Admin/Manufacturer/DeleteSelected"

    @staticmethod
    def edit_page(manufacturer_id: int) -> str:
        return f"/Admin/Manufacturer/Edit/{manufacturer_id}"

    @staticmethod
    def delete(manufacturer_id: int) -> str:
        return f"/Admin/Manufacturer/Delete/{manufacturer_id}"


MANUFACTURERS_ENDPOINTS = ManufacturersEndpoints()
