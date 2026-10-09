from typing import Any


def success_response(
    data: Any = None,
    message: str = "Success",
) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": False,
        "message": message,
        "data": data,
    }


def paginated_response(
    data: list,
    page: int,
    page_size: int,
    total: int,
) -> dict:
    total_pages = (
        (total + page_size - 1) // page_size
        if page_size > 0
        else 0
    )

    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }