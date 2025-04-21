import os
from vector_db import VectorDB
import google.generativeai as genai

# --- Gemini Setup ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyC8HXle9cYzDpopPvAnBjNxs6BLtqC4gls"  # Replace with your API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- Vector DB Setup ---
vdb = VectorDB(csv_path="data/chunks.csv")  # Adjust path as needed

def generate_gemini_response(question: str, context: str) -> str:
    """
    Calls Gemini API with a structured prompt and retrieves the response.
    """
    prompt = f"""
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
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating Gemini response: {str(e)}"

def process_question(question: str):
    """
    Main function to handle the chatbot pipeline.
    """
    print("\nProcessing the question...")

    # Step 1: Retrieve relevant context from the Vector DB
    retrieved_chunks = vdb.query(question, n_results=5)
    context = "\n".join(retrieved_chunks)

    # Step 2: Generate response using Gemini (final answer generation)
    answer = generate_gemini_response(question, context)

    # Step 3: Output the final answer to the user
    print("\nAnswer:")
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
