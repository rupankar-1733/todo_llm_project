from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium" 
    high = "high"
    urgent = "urgent"

class Category(str, Enum):
    work = "work"
    personal = "personal"
    shopping = "shopping"
    health = "health"
    education = "education"
    finance = "finance"
    travel = "travel"
    home = "home"
    other = "other"

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    category: Optional[Category] = Category.other
    priority: Optional[Priority] = Priority.medium
    due_date: Optional[str] = None  # Format: "2025-01-15"
    status: Optional[TaskStatus] = TaskStatus.pending
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[List[str]] = []
    estimated_hours: Optional[float] = None
    completed_at: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[Category] = Category.other
    priority: Optional[Priority] = Priority.medium
    due_date: Optional[str] = None
    tags: Optional[List[str]] = []
    estimated_hours: Optional[float] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    due_date: Optional[str] = None
    status: Optional[TaskStatus] = None
    tags: Optional[List[str]] = None
    estimated_hours: Optional[float] = None

class TaskFilter(BaseModel):
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    due_before: Optional[str] = None
    due_after: Optional[str] = None
    tags: Optional[List[str]] = []
