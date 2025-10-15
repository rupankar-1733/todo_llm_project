from typing import Dict, List, Any, Callable
from app.storage import storage
from app.models import Task, TaskCreate, TaskUpdate, TaskFilter, Priority, Category, TaskStatus
from app.vector_db import vector_db
from app.auth import get_password_hash, verify_password, create_access_token
from datetime import datetime, timedelta
import json

class MCPTool:
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function

class TodoMCPServer:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.task_id_counter = max([task.id for tasks in storage.tasks_db.values() for task in tasks], default=0) + 1
        
        # Register MCP tools
        self.register_tools()
    
    def tool(self, name: str, description: str = ""):
        """Decorator to register MCP tools"""
        def decorator(func):
            self.tools[name] = MCPTool(name, description, func)
            return func
        return decorator
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool by name with arguments"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        try:
            result = self.tools[tool_name].function(**kwargs)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_tools(self) -> Dict[str, Any]:
        """List all available tools"""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in self.tools.values()
            ]
        }
    
    def register_tools(self):
        """Register all available tools for the LLM to use"""
        
        @self.tool("register_user", "Register a new user account")
        def register_user(username: str, password: str) -> Dict[str, Any]:
            if username in storage.users_db:
                return {"success": False, "error": "Username already registered"}
            
            hashed_password = get_password_hash(password)
            storage.add_user(username, {"username": username, "hashed_password": hashed_password})
            return {"success": True, "message": "User registered successfully"}
        
        @self.tool("login_user", "Login user and return access token")
        def login_user(username: str, password: str) -> Dict[str, Any]:
            db_user = storage.users_db.get(username)
            if not db_user or not verify_password(password, db_user["hashed_password"]):
                return {"success": False, "error": "Invalid username or password"}
            
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer"
            }
        
        @self.tool("create_task", "Create a new task with categories, priorities, and due dates")
        def create_task(username: str, title: str, description: str = "", 
                       category: str = "other", priority: str = "medium", 
                       due_date: str = None, tags: List[str] = None, 
                       estimated_hours: float = None) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            # Create enhanced task
            task = Task(
                id=self.task_id_counter,
                title=title,
                description=description,
                category=Category(category) if category else Category.other,
                priority=Priority(priority) if priority else Priority.medium,
                due_date=due_date,
                tags=tags or [],
                estimated_hours=estimated_hours,
                status=TaskStatus.pending
            )
            self.task_id_counter += 1
            
            # Add to persistent storage
            storage.add_task(username, task)
            
            # Add to vector database for semantic search
            search_text = f"{title} {description} {category} {' '.join(tags or [])}"
            vector_db.add_task(task.id, title, search_text)
            
            return {
                "success": True,
                "task": task.dict()
            }
        
        @self.tool("update_task", "Update an existing task")
        def update_task(username: str, task_id: int, title: str = None,
                       description: str = None, category: str = None,
                       priority: str = None, status: str = None,
                       due_date: str = None, tags: List[str] = None,
                       estimated_hours: float = None) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            user_tasks = storage.tasks_db.get(username, [])
            task_to_update = None
            
            for task in user_tasks:
                if task.id == task_id:
                    task_to_update = task
                    break
            
            if not task_to_update:
                return {"success": False, "error": "Task not found"}
            
            # Update fields if provided
            if title: task_to_update.title = title
            if description is not None: task_to_update.description = description
            if category: task_to_update.category = Category(category)
            if priority: task_to_update.priority = Priority(priority)
            if status: 
                task_to_update.status = TaskStatus(status)
                if status == "completed":
                    task_to_update.completed_at = datetime.now().isoformat()
            if due_date is not None: task_to_update.due_date = due_date
            if tags is not None: task_to_update.tags = tags
            if estimated_hours is not None: task_to_update.estimated_hours = estimated_hours
            
            # Update in storage
            storage.update_task(username, task_id, task_to_update)
            
            return {"success": True, "task": task_to_update.dict()}
        
        @self.tool("get_tasks", "Get all tasks for a user with optional filtering")
        def get_tasks(username: str, category: str = None, priority: str = None,
                     status: str = None, limit: int = 50) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            user_tasks = storage.tasks_db.get(username, [])
            
            # Apply filters
            filtered_tasks = user_tasks
            if category:
                filtered_tasks = [t for t in filtered_tasks if t.category == category]
            if priority:
                filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
            if status:
                filtered_tasks = [t for t in filtered_tasks if t.status == status]
            
            # Sort by priority and due date
            priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
            filtered_tasks.sort(key=lambda t: (
                priority_order.get(t.priority, 0),
                t.due_date or "9999-12-31"
            ), reverse=True)
            
            # Limit results
            filtered_tasks = filtered_tasks[:limit]
            
            tasks_data = [task.dict() for task in filtered_tasks]
            
            return {"success": True, "tasks": tasks_data, "count": len(tasks_data)}
        
        @self.tool("search_tasks", "Search tasks using semantic similarity with advanced filtering")
        def search_tasks(username: str, query: str, category: str = None,
                        priority: str = None, status: str = None, limit: int = 10) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            results = vector_db.search_tasks(query, k=limit * 3)  # Get more for filtering
            
            # Filter results to only include current user's tasks
            user_tasks = storage.tasks_db.get(username, [])
            user_task_dict = {task.id: task for task in user_tasks}
            
            filtered_results = []
            for result in results:
                task_id = result['task_id']
                if task_id in user_task_dict:
                    task = user_task_dict[task_id]
                    
                    # Apply additional filters
                    if category and task.category != category:
                        continue
                    if priority and task.priority != priority:
                        continue
                    if status and task.status != status:
                        continue
                    
                    result['task_details'] = task.dict()
                    filtered_results.append(result)
            
            # Limit final results
            filtered_results = filtered_results[:limit]
            
            return {
                "success": True,
                "query": query,
                "results": filtered_results,
                "count": len(filtered_results)
            }
        
        @self.tool("delete_task", "Delete a task by ID")
        def delete_task(username: str, task_id: int) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            user_tasks = storage.tasks_db.get(username, [])
            filtered_tasks = [task for task in user_tasks if task.id != task_id]
            
            if len(filtered_tasks) == len(user_tasks):
                return {"success": False, "error": "Task not found"}
            
            storage.update_tasks(username, filtered_tasks)
            return {"success": True, "message": f"Task {task_id} deleted"}
        
        @self.tool("get_user_stats", "Get user task statistics and analytics")
        def get_user_stats(username: str) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            stats = storage.get_user_stats(username)
            user_tasks = storage.tasks_db.get(username, [])
            
            # Category breakdown
            category_stats = {}
            for task in user_tasks:
                cat = task.category
                if cat not in category_stats:
                    category_stats[cat] = {"total": 0, "completed": 0}
                category_stats[cat]["total"] += 1
                if task.status == "completed":
                    category_stats[cat]["completed"] += 1
            
            # Priority breakdown
            priority_stats = {}
            for task in user_tasks:
                pri = task.priority
                if pri not in priority_stats:
                    priority_stats[pri] = {"total": 0, "completed": 0}
                priority_stats[pri]["total"] += 1
                if task.status == "completed":
                    priority_stats[pri]["completed"] += 1
            
            return {
                "success": True,
                "stats": {
                    **stats,
                    "category_breakdown": category_stats,
                    "priority_breakdown": priority_stats
                }
            }
        
        @self.tool("get_due_soon", "Get tasks due within specified days")
        def get_due_soon(username: str, days: int = 7) -> Dict[str, Any]:
            if username not in storage.users_db:
                return {"success": False, "error": "User not found"}
            
            user_tasks = storage.tasks_db.get(username, [])
            today = datetime.now().date()
            cutoff_date = today + timedelta(days=days)
            
            due_soon = []
            overdue = []
            
            for task in user_tasks:
                if task.due_date and task.status != "completed":
                    try:
                        task_date = datetime.fromisoformat(task.due_date).date()
                        if task_date < today:
                            overdue.append(task.dict())
                        elif task_date <= cutoff_date:
                            due_soon.append(task.dict())
                    except ValueError:
                        continue
            
            # Sort by due date
            due_soon.sort(key=lambda t: t['due_date'])
            overdue.sort(key=lambda t: t['due_date'])
            
            return {
                "success": True,
                "due_soon": due_soon,
                "overdue": overdue,
                "due_soon_count": len(due_soon),
                "overdue_count": len(overdue)
            }

# Global MCP server instance
mcp_server = TodoMCPServer()
