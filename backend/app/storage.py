import json
import os
from typing import Dict, List, Any
from datetime import datetime
from app.models import Task

class PersistentStorage:
    def __init__(self, users_file='data/users.json', tasks_file='data/tasks.json'):
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        
        self.users_file = users_file
        self.tasks_file = tasks_file
        
        # Load existing data
        self.users_db = self.load_users()
        self.tasks_db = self.load_tasks()
    
    def load_users(self) -> Dict[str, Dict]:
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users_db, f, indent=2)
    
    def load_tasks(self) -> Dict[str, List]:
        """Load tasks from JSON file"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
                # Convert task dicts back to Task objects
                for username in data:
                    tasks_list = []
                    for task_data in data[username]:
                        # Handle backward compatibility
                        if isinstance(task_data, dict):
                            # Add default values for new fields
                            task_data.setdefault('category', 'other')
                            task_data.setdefault('priority', 'medium')
                            task_data.setdefault('status', 'pending')
                            task_data.setdefault('tags', [])
                            task_data.setdefault('created_at', datetime.now().isoformat())
                            task_data.setdefault('updated_at', datetime.now().isoformat())
                            tasks_list.append(Task(**task_data))
                    data[username] = tasks_list
                return data
        return {}
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        # Convert Task objects to dicts for JSON serialization
        serializable_data = {}
        for username, tasks in self.tasks_db.items():
            serializable_data[username] = []
            for task in tasks:
                if isinstance(task, Task):
                    serializable_data[username].append(task.dict())
                else:
                    serializable_data[username].append(task)
        
        with open(self.tasks_file, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=str)
    
    def add_user(self, username: str, user_data: Dict):
        """Add a new user and save to file"""
        self.users_db[username] = user_data
        self.save_users()
    
    def add_task(self, username: str, task: Task):
        """Add a task for a user and save to file"""
        if username not in self.tasks_db:
            self.tasks_db[username] = []
        
        # Set timestamps
        now = datetime.now().isoformat()
        task.created_at = now
        task.updated_at = now
        
        self.tasks_db[username].append(task)
        self.save_tasks()
    
    def update_task(self, username: str, task_id: int, updated_task: Task):
        """Update a specific task"""
        if username in self.tasks_db:
            for i, task in enumerate(self.tasks_db[username]):
                if task.id == task_id:
                    updated_task.updated_at = datetime.now().isoformat()
                    self.tasks_db[username][i] = updated_task
                    self.save_tasks()
                    return True
        return False
    
    def update_tasks(self, username: str, tasks: List[Task]):
        """Update all tasks for a user and save to file"""
        self.tasks_db[username] = tasks
        self.save_tasks()
    
    # Add demo user on startup
    def init_demo_account():
        from app.auth import get_password_hash
        if "demo" not in storage.users_db:
            storage.users_db["demo"] = {
                "username": "demo",
                "hashed_password": get_password_hash("demo123")
            }
            
    def get_user_stats(self, username: str) -> Dict:
        """Get user task statistics"""
        if username not in self.tasks_db:
            return {}
        
        tasks = self.tasks_db[username]
        total = len(tasks)
        completed = len([t for t in tasks if t.status == 'completed'])
        pending = len([t for t in tasks if t.status == 'pending'])
        in_progress = len([t for t in tasks if t.status == 'in_progress'])
        overdue = len([t for t in tasks if t.due_date and t.due_date < datetime.now().date().isoformat() and t.status != 'completed'])
        
        return {
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'overdue': overdue,
            'completion_rate': round(completed / total * 100, 1) if total > 0 else 0
        }

# Global storage instance
storage = PersistentStorage()
