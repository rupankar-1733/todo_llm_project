from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.vector_db import vector_db
from app.storage import storage
from app.models import UserCreate, Token, Task, TaskCreate, TaskUpdate, TaskFilter
from app.auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from app.mcp_server import mcp_server
from app.llm_service import llm_service
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Advanced Todo LLM Project", 
    version="2.0.0",
    description="AI-powered task management with categories, priorities, due dates, and semantic search"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://todo-j7mqfv6e5-rupankar-mondals-projects.vercel.app",
        "https://*.vercel.app",  ], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use persistent storage
fake_users_db = storage.users_db
tasks_db = storage.tasks_db
task_id_counter = max([task.id for tasks in tasks_db.values() for task in tasks], default=0) + 1

# OAuth2 scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic models for API
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

class TaskFilterRequest(BaseModel):
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    limit: Optional[int] = 50

# Helper to get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

@app.get("/")
async def root():
    return {
        "message": "Advanced Todo LLM Project with Enhanced Features!",
        "version": "2.0.0",
        "features": [
            "Categories & Priorities",
            "Due Dates & Reminders", 
            "Task Analytics",
            "Semantic Search",
            "LLM Integration",
            "MCP Backend"
        ],
        "mcp_available": True
    }

@app.post("/chat")
async def chat_with_llm(request: ChatRequest, username: str = Depends(get_current_user)):
    """Conversational chat with LLM for todo/task actions only."""

    # Get available tools (unchanged)
    tools_info = mcp_server.list_tools()

    # Get current date context (still used for LLM if it needs dates)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    today_readable = now.strftime("%B %d, %Y")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    days_until_saturday = (5 - now.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    this_weekend = (now + timedelta(days=days_until_saturday)).strftime("%Y-%m-%d")

    # STRICT SYSTEM PROMPT:
    system_message = {
        "role": "system",
        "content": (
            "You are a todo-list chatbot. Only respond to messages that ask you to create, search, update, complete, "
            "or delete tasks. If the user says hello, hi, or anything not related to todos, politely say you are only "
            "for todo tasks and show these prompt examples:\n"
            "  • Add a high priority task to buy groceries tomorrow\n"
            "  • What work tasks are due this week?\n"
            "  • Mark 'call mom' as done\n"
            "  • Delete my 'gym' task\n"
            "\n"
            f"Today's date is: {today_readable} ({today})\n"
            f"Tomorrow is: {tomorrow}\n"
            f"Next week (7 days from now) is: {next_week}\n"
            f"This weekend (Saturday) is: {this_weekend}\n"
            f"Current user: {username}\n"
            "Always respond only with relevant task actions or a helpful fallback if the intent is not about todo management.\n"
        )
    }

    # Prepend the system message
    full_messages = [system_message] + request.messages

    # LLM chat with MCP tool support (unchanged)
    llm_response = llm_service.chat_with_tools(full_messages, tools_info["tools"])

    if not llm_response["success"]:
        raise HTTPException(status_code=500, detail=llm_response["error"])

    # (unchanged: if LLM calls tools, use the tool logic)
    if llm_response["tool_calls"]:
        tool_results = []
        for tool_call in llm_response["tool_calls"]:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = mcp_server.call_tool(tool_name, **tool_args)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "result": result
            })

        return {
            "message": llm_response["message"].content or "I've executed the requested actions.",
            "tool_calls": llm_response["tool_calls"],
            "tool_results": tool_results
        }

    return {
        "message": llm_response["message"].content,
        "tool_calls": None,
        "tool_results": None
    }

# Enhanced REST endpoints for compatibility
@app.post("/register")
async def register(user: UserCreate):
    result = mcp_server.call_tool("register_user", username=user.username, password=user.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": result["message"]}

@app.post("/login", response_model=Token)
async def login(user: UserCreate):
    result = mcp_server.call_tool("login_user", username=user.username, password=user.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"access_token": result["access_token"], "token_type": result["token_type"]}

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, username: str = Depends(get_current_user)):
    result = mcp_server.call_tool(
        "create_task", 
        username=username, 
        title=task.title, 
        description=task.description,
        category=task.category.value if task.category else "other",
        priority=task.priority.value if task.priority else "medium",
        due_date=task.due_date,
        tags=task.tags,
        estimated_hours=task.estimated_hours
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result["task"]

@app.get("/tasks")
def read_tasks(filter_req: TaskFilterRequest = Depends(), username: str = Depends(get_current_user)):
    result = mcp_server.call_tool(
        "get_tasks", 
        username=username,
        category=filter_req.category,
        priority=filter_req.priority,
        status=filter_req.status,
        limit=filter_req.limit
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"tasks": result["tasks"], "count": result["count"]}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, username: str = Depends(get_current_user)):
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    if update_data:
        # Convert enums to strings
        if 'category' in update_data:
            update_data['category'] = update_data['category'].value
        if 'priority' in update_data:
            update_data['priority'] = update_data['priority'].value
        if 'status' in update_data:
            update_data['status'] = update_data['status'].value
            
        result = mcp_server.call_tool("update_task", username=username, task_id=task_id, **update_data)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result["task"]
    else:
        raise HTTPException(status_code=400, detail="No fields to update")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, username: str = Depends(get_current_user)):
    result = mcp_server.call_tool("delete_task", username=username, task_id=task_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

@app.get("/tasks/search")
def search_tasks(query: str, category: str = None, priority: str = None, 
                status: str = None, limit: int = 10, username: str = Depends(get_current_user)):
    result = mcp_server.call_tool(
        "search_tasks", 
        username=username, 
        query=query, 
        category=category,
        priority=priority,
        status=status,
        limit=limit
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"query": result["query"], "results": result["results"], "count": result["count"]}

@app.get("/stats")
def get_user_stats(username: str = Depends(get_current_user)):
    """Get comprehensive user statistics"""
    result = mcp_server.call_tool("get_user_stats", username=username)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result["stats"]

@app.get("/due-soon")
def get_due_soon(days: int = 7, username: str = Depends(get_current_user)):
    """Get tasks due soon and overdue tasks"""
    result = mcp_server.call_tool("get_due_soon", username=username, days=days)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# MCP endpoints for LLM integration
@app.post("/mcp/call/{tool_name}")
async def mcp_call(tool_name: str, request_data: dict):
    """Direct MCP tool calling endpoint for LLM frontend"""
    result = mcp_server.call_tool(tool_name, **request_data)
    return result

@app.get("/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools for the LLM"""
    return mcp_server.list_tools()
