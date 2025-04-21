import os
from dotenv import load_dotenv
from vector_db import VectorDB
import google.generativeai as genai

# --- Load environment variables securely ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY not set. Please add it to your .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- Vector DB Setup ---
vdb = VectorDB(csv_path="../data/chunks.csv")  # Adjust path as needed

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

def process_question(question: str):
    print("\nProcessing the question...")

    # Step 1: Retrieve relevant context from the Vector DB
    retrieved_chunks = vdb.query(question, n_results=5)
    if not retrieved_chunks or all(not c.strip() for c in retrieved_chunks):
        print("No relevant context found for your question. Please try rephrasing.")
        return

    context = "\n".join(retrieved_chunks)

    # Step 2: Generate response using Gemini (final answer generation)
    answer = generate_gemini_response(question, context)

    # Step 3: Output the final answer to the user
    print("\n--- Context Used ---")
    print(context)
    print("\n--- Answer ---")
    print(answer)

if __name__ == "__main__":
    print("FutureMinds chatbot is ready. Ask a question (type 'exit' to quit).")
    while True:
        question = input("\nYour question: ")
        if question.lower() == 'exit':
            print("\nExiting chatbot...")
            break
        else:
            process_question(question)
