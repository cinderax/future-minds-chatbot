from flask import Flask, render_template, request, jsonify
import os
import sys
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.append("agents")

# Import agents
from agents.history_agent import HistoryQuestionAnswerer
from agents.translator_agent import TranslatorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.planner_agent import PlannerAgent
from agents.todo_agent import TodoAgent

app = Flask(__name__)

# Initialize ChromaDB client
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "processed_data/chroma_db")
client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH,
    settings=Settings(allow_reset=True, is_persistent=True)
)

# Initialize agents
history_agent = HistoryQuestionAnswerer(client=client, collection_name="textbook")
translator_agent = TranslatorAgent()
summarizer_agent = SummarizerAgent()
planner_agent = PlannerAgent()
todo_agent = TodoAgent()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/translator')
def translator():
    return render_template('translator.html')


@app.route('/summarizer')
def summarizer():
    return render_template('summarizer.html')


@app.route('/planner')
def planner():
    return render_template('planner.html')


@app.route('/todo')
def todo():
    return render_template('todo.html')


@app.route('/api/history/answer', methods=['POST'])
def get_history_answer():
    data = request.json
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        result = history_agent.answer_question(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        result = translator_agent.translate(text, target_language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    data = request.json
    text = data.get('text', '')
    length = data.get('length', 'medium')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        result = summarizer_agent.summarize(text, length)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/plan', methods=['POST'])
def create_plan():
    data = request.json
    goal = data.get('goal', '')
    deadline = data.get('deadline', '')
    
    if not goal:
        return jsonify({"error": "No goal provided"}), 400
    
    try:
        result = planner_agent.create_plan(goal, deadline)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/todo/add', methods=['POST'])
def add_todo():
    data = request.json
    task = data.get('task', '')
    due_date = data.get('due_date', '')
    priority = data.get('priority', 'medium')
    
    if not task:
        return jsonify({"error": "No task provided"}), 400
    
    try:
        result = todo_agent.add_task(task, due_date, priority)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/todo/get', methods=['GET'])
def get_todos():
    try:
        todos = todo_agent.get_tasks()
        return jsonify({"todos": todos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/todo/update', methods=['POST'])
def update_todo():
    data = request.json
    task_id = data.get('id', '')
    completed = data.get('completed', False)
    
    if not task_id:
        return jsonify({"error": "No task ID provided"}), 400
    
    try:
        result = todo_agent.update_task(task_id, completed)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/todo/delete', methods=['POST'])
def delete_todo():
    data = request.json
    task_id = data.get('id', '')
    
    if not task_id:
        return jsonify({"error": "No task ID provided"}), 400
    
    try:
        result = todo_agent.delete_task(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
#uvicorn app:app --reload