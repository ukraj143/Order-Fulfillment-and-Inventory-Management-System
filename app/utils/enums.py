from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    FULFILLMENT_AGENT = "Fulfillment Agent"
    CUSTOMER = "Customer"


class OrderStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    PROCESSING = "Processing"
    FULFILLED = "Fulfilled"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class FulfillmentStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class ReturnStatus(str, Enum):
    REQUESTED = "Requested"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PROCESSED = "Processed"


class ReservationStatus(str, Enum):
    RESERVED = "Reserved"
    RELEASED = "Released"
    FULFILLED = "Fulfilled"


class InventoryTransactionType(str, Enum):
    RECEIPT = "Receipt"
    ISSUE = "Issue"
    RESERVATION = "Reservation"
    RELEASE = "Release"
    ADJUSTMENT = "Adjustment"