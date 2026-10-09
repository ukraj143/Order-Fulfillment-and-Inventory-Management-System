from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.fulfillment import FulfillmentCreate, FulfillmentResponse, FulfillmentUpdate
from app.services.fulfillment_service import FulfillmentService

router = APIRouter(prefix="/fulfillments", tags=["Fulfillment"])


@router.get("/", response_model=list[FulfillmentResponse])
def list_fulfillments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FulfillmentService(db).get_all()


@router.post(
    "/",
    response_model=FulfillmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fulfillment(
    data: FulfillmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager")
    ),
):
    return FulfillmentService(db).create(data)


@router.get("/{fulfillment_id}", response_model=FulfillmentResponse)
def get_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FulfillmentService(db).get(fulfillment_id)


@router.put("/{fulfillment_id}", response_model=FulfillmentResponse)
def update_fulfillment(
    fulfillment_id: int,
    data: FulfillmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FulfillmentService(db).update(
        fulfillment_id=fulfillment_id,
        data=data,
    )


@router.post(
    "/{fulfillment_id}/assign/{agent_id}",
    response_model=FulfillmentResponse,
)
def assign_fulfillment_agent(
    fulfillment_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager")
    ),
):
    return FulfillmentService(db).assign_agent(
        fulfillment_id=fulfillment_id,
        agent_id=agent_id,
    )


@router.post(
    "/{fulfillment_id}/reassign/{agent_id}",
    response_model=FulfillmentResponse,
)
def reassign_fulfillment_agent(
    fulfillment_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager")
    ),
):
    return FulfillmentService(db).reassign_agent(
        fulfillment_id=fulfillment_id,
        agent_id=agent_id,
    )


@router.post(
    "/{fulfillment_id}/accept",
    response_model=FulfillmentResponse,
)
def accept_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager", "Fulfillment Agent")
    ),
):
    return FulfillmentService(db).accept(fulfillment_id)


@router.post(
    "/{fulfillment_id}/process",
    response_model=FulfillmentResponse,
)
def process_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager", "Fulfillment Agent")
    ),
):
    return FulfillmentService(db).process(fulfillment_id)


@router.post(
    "/{fulfillment_id}/pack",
    response_model=FulfillmentResponse,
)
def pack_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager", "Fulfillment Agent")
    ),
):
    return FulfillmentService(db).pack(fulfillment_id)


@router.post(
    "/{fulfillment_id}/ship",
    response_model=FulfillmentResponse,
)
def ship_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager", "Fulfillment Agent")
    ),
):
    return FulfillmentService(db).ship(fulfillment_id)


@router.post(
    "/{fulfillment_id}/deliver",
    response_model=FulfillmentResponse,
)
def deliver_fulfillment(
    fulfillment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Admin", "Warehouse Manager", "Fulfillment Agent")
    ),
):
    return FulfillmentService(db).deliver(fulfillment_id)
