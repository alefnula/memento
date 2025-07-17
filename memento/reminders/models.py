from typing import Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Calendar:
    """Represents a calendar with its properties."""
    id: str
    title: str
    color: Optional[str] = None
    allows_modifications: bool = True
    is_subscribed: bool = False


@dataclass
class Reminder:
    """Represents a reminder with all its properties."""
    id: str
    title: str
    notes: str
    completed: bool = False
    creation_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    priority: int = 0
    calendar: Optional[str] = None
    url: Optional[str] = None
