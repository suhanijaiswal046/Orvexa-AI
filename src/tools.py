"""Company demo tools. Replace in-memory demo records with approved APIs in production."""
from langchain_core.tools import tool

ORDERS_DB = {
    "ORD-1001": {"status": "Shipped", "eta": "2026-11-02", "item": "CloudSync Pro License (5 seats)"},
    "ORD-1002": {"status": "Processing", "eta": "2026-11-05", "item": "CloudSync Business License (20 seats)"},
    "ORD-1003": {"status": "Delivered", "eta": "2026-10-25", "item": "CloudSync Enterprise Setup Package"},
}
TICKETS_DB = {
    "TKT-5001": {"status": "Open", "subject": "SSO login loop on Chrome", "assigned_to": "Riya Sharma"},
    "TKT-5002": {"status": "In Progress", "subject": "Files not syncing on macOS", "assigned_to": "James Lee"},
    "TKT-5003": {"status": "Resolved", "subject": "Billing discrepancy", "assigned_to": "Priya Patel"},
}

@tool
def get_order_status(order_id: str) -> str:
    """Look up a demo order using an ID such as ORD-1001."""
    key = order_id.strip().upper()
    item = ORDERS_DB.get(key)
    if not item:
        return f"No demo order found for {key}. Check the ID."
    return f"Order {key}: {item['item']} | Status: {item['status']} | ETA: {item['eta']}"

@tool
def get_ticket_status(ticket_id: str) -> str:
    """Look up a demo support ticket using an ID such as TKT-5001."""
    key = ticket_id.strip().upper()
    item = TICKETS_DB.get(key)
    if not item:
        return f"No demo ticket found for {key}. Check the ID."
    return f"Ticket {key}: {item['subject']} | Status: {item['status']} | Assigned to: {item['assigned_to']}"

all_tools = [get_order_status, get_ticket_status]
