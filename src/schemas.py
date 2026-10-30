"""Pydantic schemas used by routing, ticket creation, and analytics."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    route: Literal["knowledge", "support", "analytics", "general"] = Field(
        description="Best destination for the user's latest request."
    )
    reason: str = Field(description="Short explanation for the routing decision.")

class TicketInfo(BaseModel):
    name: str = Field(default="Unknown", description="Customer name, or Unknown.")
    issue: str = Field(description="Short, clear description of the reported issue.")
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Urgency of the issue."
    )

class AnalyticsRequest(BaseModel):
    operation: Literal["overview", "sum", "mean", "max", "min", "top", "value_counts", "correlation"] = "overview"
    column: Optional[str] = None
    group_by: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=20)
