import os
import uuid
from datetime import datetime

class TodoAgent:
    def __init__(self):
        """
        Initialize the TodoAgent.
        
        This is a simple in-memory implementation.
        In a production app, you'd use a database.
        """
        # Dictionary to store tasks
        self.tasks = {}

    def add_task(self, task_description, due_date=None, priority="medium"):
        """
        Add a new task to the to-do list.

        Args:
            task_description (str): Description of the task.
            due_date (str): Optional due date for the task.
            priority (str): Task priority (low, medium, high).

        Returns:
            dict: The created task object.
        """
        if not task_description:
            return {"error": "Task description is required"}
            
        # Validate priority
        if priority not in ["low", "medium", "high"]:
            priority = "medium"
            
        # Create task ID
        task_id = str(uuid.uuid4())
        created_date = datetime.now().isoformat()
        
        # Create task object
        task = {
            "id": task_id,
            "description": task_description,
            "due_date": due_date,
            "priority": priority,
            "completed": False,
            "created_at": created_date,
            "completed_at": None
        }
        
        # Add to tasks dictionary
        self.tasks[task_id] = task
        
        return task

    def get_tasks(self, include_completed=True):
        """
        Get all tasks in the to-do list.

        Args:
            include_completed (bool): Whether to include completed tasks.

        Returns:
            list: List of task objects.
        """
        if include_completed:
            return list(self.tasks.values())
        else:
            return [task for task in self.tasks.values() if not task["completed"]]

    def update_task(self, task_id, completed=None):
        """
        Update a task in the to-do list.

        Args:
            task_id (str): ID of the task to update.
            completed (bool): Whether the task is completed.

        Returns:
            dict: The updated task object or error.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with ID {task_id} not found"}
            
        task = self.tasks[task_id]
        
        # Update completion status if provided
        if completed is not None:
            task["completed"] = completed
            if completed:
                task["completed_at"] = datetime.now().isoformat()
            else:
                task["completed_at"] = None
        
        return task

    def delete_task(self, task_id):
        """
        Delete a task from the to-do list.

        Args:
            task_id (str): ID of the task to delete.

        Returns:
            dict: Success message or error.
        """
        if task_id not in self.tasks:
            return {"error": f"Task with ID {task_id} not found"}
            
        # Remove the task
        del self.tasks[task_id]
        
        return {"success": True, "message": f"Task {task_id} deleted successfully"}