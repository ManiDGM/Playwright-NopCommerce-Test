"""URL path constants for admin Category MVC/AJAX endpoints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriesEndpoints:
    LIST_PAGE: str = "/Admin/Category/List"
    LIST: str = "/Admin/Category/List"
    CREATE_PAGE: str = "/Admin/Category/Create"
    CREATE: str = "/Admin/Category/Create"
    EDIT_PAGE: str = "/Admin/Category/Edit/{category_id}"
    EDIT: str = "/Admin/Category/Edit"
    DELETE: str = "/Admin/Category/Delete/{category_id}"
    DELETE_SELECTED: str = "/Admin/Category/DeleteSelected"

    @staticmethod
    def edit_page(category_id: int) -> str:
        return f"/Admin/Category/Edit/{category_id}"

    @staticmethod
    def delete(category_id: int) -> str:
        return f"/Admin/Category/Delete/{category_id}"


CATEGORIES_ENDPOINTS = CategoriesEndpoints()
