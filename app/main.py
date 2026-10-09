from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app = FastAPI(
    title="Order Fulfillment & Inventory Management Platform",
    description=(
        "Backend API for order fulfillment, inventory management, "
        "warehouse operations, returns, notifications, and reporting."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(fulfillment_router)
app.include_router(returns_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)
app.include_router(reports_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Order Fulfillment & Inventory Management Platform API is running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
    }