from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


# DATABASE TABLE SCHEMA: Represents exactly how the data looks inside PostgreSQL
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# INBOUND DATA SCHEMA: Validates what fields the frontend is allowed to send us
class ProjectCreate(SQLModel):
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
