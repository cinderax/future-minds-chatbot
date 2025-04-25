
import os
from dotenv import load_dotenv
import google.generativeai as genai
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

class PlannerAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Initialize the PlannerAgent.

        Args:
            model_name (str): Gemini model name.
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=google_api_key)

        self.model = genai.GenerativeModel(model_name)
        
        self.plans = {}

    def create_plan(self, goal, deadline=None):
        """
        Creates a detailed plan to achieve the specified goal by the deadline.

        Args:
            goal (str): The goal to achieve.
            deadline (str): The deadline for achieving the goal (optional).

        Returns:
            dict: A structured plan with steps, timeline, and resources.
        """
        if not goal:
            return {"error": "No goal provided"}
            
        deadline_str = f" by {deadline}" if deadline else ""
            
        prompt = f"""
Create a detailed action plan to achieve the following goal{deadline_str}:
Goal: {goal}

Please include:
1. A breakdown of the main steps required
2. A suggested timeline for each step
3. Any resources, tools, or skills needed
4. Potential challenges and how to overcome them
5. Key milestones to track progress

Please format the plan with:

- Clear markdown headings and subheadings
- Numbered steps and timelines
- Bold important points and milestones
- A table summarizing the timeline
- Short, concise paragraphs for readability
- A summary section with key takeaways at the end

Make the output professional and visually appealing.
"""

        response = self.model.generate_content(prompt)
        plan_text = response.text.strip()
        
        # Create a structured plan
        plan_id = str(uuid.uuid4())
        created_date = datetime.now().isoformat()
        
        plan = {
            "id": plan_id,
            "goal": goal,
            "deadline": deadline,
            "plan_text": plan_text,
            "created_at": created_date
        }
        
        # Store the plan
        self.plans[plan_id] = plan
        
        return plan