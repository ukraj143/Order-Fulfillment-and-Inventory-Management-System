from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/dashboard")
def dashboard_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return ReportService(db).dashboard()


@router.get("/orders")
def order_status_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
            "Fulfillment Agent",
        )
    ),
):
    return ReportService(db).order_status_report()


@router.get("/inventory")
def inventory_report(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Warehouse Manager",
        )
    ),
):
    return ReportService(db).inventory_report()


@router.get("/sales")
def sales_report(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    return ReportService(db).sales_report()