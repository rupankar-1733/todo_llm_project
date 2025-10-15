from groq import Groq
from typing import Dict, List, Any
import os
import json
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

class LLMService:
    def __init__(self, api_key: str = None):
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables or passed as parameter")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def chat_with_tools(self, messages: List[Dict], available_tools: List[Dict]) -> Dict[str, Any]:
        """Chat with LLM and let it call MCP tools"""
        try:
            # Convert MCP tools to Groq function calling format
            groq_tools = self._convert_mcp_tools_to_groq(available_tools)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=groq_tools,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1500
            )
            
            return {
                "success": True,
                "message": response.choices[0].message,
                "tool_calls": response.choices[0].message.tool_calls
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_mcp_tools_to_groq(self, mcp_tools: List[Dict]) -> List[Dict]:
        """Convert MCP tool format to Groq function calling format"""
        tool_schemas = {
            "create_task": {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task with categories, priorities, due dates, and tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string", "description": "Detailed task description"},
                            "category": {
                                "type": "string", 
                                "enum": ["work", "personal", "shopping", "health", "education", "finance", "travel", "home", "other"],
                                "description": "Task category"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Task priority level"
                            },
                            "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags for the task"
                            },
                            "estimated_hours": {"type": "number", "description": "Estimated hours to complete"}
                        },
                        "required": ["username", "title"]
                    }
                }
            },
            "update_task": {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task including status changes",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "task_id": {"type": "integer", "description": "Task ID to update"},
                            "title": {"type": "string", "description": "New task title"},
                            "description": {"type": "string", "description": "New task description"},
                            "category": {
                                "type": "string",
                                "enum": ["work", "personal", "shopping", "health", "education", "finance", "travel", "home", "other"],
                                "description": "New task category"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "New task priority"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "New task status"
                            },
                            "due_date": {"type": "string", "description": "New due date in YYYY-MM-DD format"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New list of tags"
                            },
                            "estimated_hours": {"type": "number", "description": "New estimated hours"}
                        },
                        "required": ["username", "task_id"]
                    }
                }
            },
            "get_tasks": {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Get all tasks with optional filtering by category, priority, or status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "category": {
                                "type": "string",
                                "enum": ["work", "personal", "shopping", "health", "education", "finance", "travel", "home", "other"],
                                "description": "Filter by category"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Filter by priority"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "Filter by status"
                            },
                            "limit": {"type": "integer", "description": "Maximum number of tasks to return", "default": 50}
                        },
                        "required": ["username"]
                    }
                }
            },
            "search_tasks": {
                "type": "function",
                "function": {
                    "name": "search_tasks",
                    "description": "Search tasks using semantic similarity with optional filtering",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "query": {"type": "string", "description": "Search query"},
                            "category": {
                                "type": "string",
                                "enum": ["work", "personal", "shopping", "health", "education", "finance", "travel", "home", "other"],
                                "description": "Filter by category"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Filter by priority"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "Filter by status"
                            },
                            "limit": {"type": "integer", "description": "Number of results", "default": 10}
                        },
                        "required": ["username", "query"]
                    }
                }
            },
            "delete_task": {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task by ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "task_id": {"type": "integer", "description": "Task ID to delete"}
                        },
                        "required": ["username", "task_id"]
                    }
                }
            },
            "get_user_stats": {
                "type": "function",
                "function": {
                    "name": "get_user_stats",
                    "description": "Get comprehensive user task statistics and analytics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"}
                        },
                        "required": ["username"]
                    }
                }
            },
            "get_due_soon": {
                "type": "function",
                "function": {
                    "name": "get_due_soon",
                    "description": "Get tasks due within specified days and overdue tasks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username"},
                            "days": {"type": "integer", "description": "Number of days to look ahead", "default": 7}
                        },
                        "required": ["username"]
                    }
                }
            }
        }
        
        groq_tools = []
        for tool in mcp_tools:
            tool_name = tool.get("name")
            if tool_name in tool_schemas:
                groq_tools.append(tool_schemas[tool_name])
        
        return groq_tools

# Initialize with explicit API key if env variable not found
try:
    llm_service = LLMService()
except ValueError:
    # Fallback to hardcoded API key for now
    llm_service = LLMService(api_key = os.getenv("GROQ_API_KEY"))
