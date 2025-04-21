import pandas as pd
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

PROMPT_TEMPLATE = """
You are FutureMinds, an elite educational assistant designed for competition-grade accuracy.

Your mission is to answer student-level questions with high clarity, precision, and alignment to the provided context only. Do not make up facts not found in the context.

---

Context (from a historical textbook):
{context}

---

Instructions:
- Think step-by-step like a teacher explaining to a curious student.
- If the context is vague or incomplete, acknowledge it.
- Never include content that is not supported by the context.
- Use simple and elegant phrasing.
- Always aim for a concise, accurate answer.
- If the question is irrelevant to the context, politely say so.

---

Student Question:
{question}

---

Your Answer (max 3-4 sentences):
"""

def generate_gemini_response(question: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating Gemini response: {str(e)}"

def batch_answer_questions(input_csv: str, output_csv: str, question_col: str = "Question", answer_col: str = "Answer"):
    # Read the questions CSV
    df = pd.read_csv(input_csv)
    answers = []

    for idx, row in df.iterrows():
        question = row[question_col]
        # Step 1: Retrieve relevant context from the Vector DB
        retrieved_chunks = vdb.query(question, n_results=5)
        context = "\n".join(retrieved_chunks)
        # Step 2: Generate answer
        answer = generate_gemini_response(question, context)
        answers.append(answer)
        print(f"Processed Q{idx+1}: {question[:50]}...")

    # Write answers to new column
    df[answer_col] = answers
    df.to_csv(output_csv, index=False)
    print(f"\nAll answers saved to: {output_csv}")

if __name__ == "__main__":
    input_csv = "data/Future-Minds-Sample-Submission.csv"  # Your input file
    output_csv = "output/Future-Minds-Submission-Answers.csv"  # Output file with answers
    batch_answer_questions(input_csv, output_csv)
