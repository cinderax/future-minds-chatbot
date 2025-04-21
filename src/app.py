from flask import Flask, request, jsonify, render_template
from vector_db import VectorDB
import google.generativeai as genai
import os

# --- Gemini Setup ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY not set in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- Vector DB Setup ---
vdb = VectorDB(csv_path="data/chunks.csv")  # Adjust path as needed

app = Flask(__name__)

PROMPT_TEMPLATE = """
You are **FutureMinds**, an elite educational assistant designed for competition-grade accuracy.

Your mission is to answer **student-level questions** with high clarity, precision, and alignment to the **provided context only**. Do **not** make up facts not found in the context.

---

📘 **Context (from a historical textbook):**
{context}

---

🎯 **Instructions:**
- Think step-by-step like a teacher explaining to a curious student.
- If the context is vague or incomplete, acknowledge it.
- Never include content that is not supported by the context.
- Use simple and elegant phrasing.
- Always aim for a concise, accurate answer.
- If the question is irrelevant to the context, politely say so.

---

❓ **Student Question:**
{question}

---

🧠 **Your Answer (max 3-4 sentences):**
"""

def generate_gemini_response(question: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating Gemini response: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')  # We'll create this next

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    retrieved_chunks = vdb.query(question, n_results=5)
    if not retrieved_chunks or all(not c.strip() for c in retrieved_chunks):
        return jsonify({'answer': "Sorry, I couldn't find relevant information for your question."})

    context = "\n".join(retrieved_chunks)
    answer = generate_gemini_response(question, context)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
