from app.routes.audit_logs import router as audit_logs_router
from app.routes.auth import router as auth_router
from app.routes.categories import router as categories_router
from app.routes.fulfillment import router as fulfillment_router
from app.routes.inventory import router as inventory_router
from app.routes.notifications import router as notifications_router
from app.routes.orders import router as orders_router
from app.routes.products import router as products_router
from app.routes.reports import router as reports_router
from app.routes.returns import router as returns_router
from app.routes.roles import router as roles_router
from app.routes.users import router as users_router
from app.routes.warehouses import router as warehouses_router


__all__ = [
    "auth_router",
    "users_router",
    "roles_router",
    "categories_router",
    "products_router",
    "warehouses_router",
    "inventory_router",
    "orders_router",
    "fulfillment_router",
    "returns_router",
    "notifications_router",
    "audit_logs_router",
    "reports_router",
]