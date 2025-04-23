import json
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
vdb = VectorDB(csv_path="outputs/chunks.csv")  # Adjust path as needed

PROMPT_TEMPLATE = """
You are Ravi’s RAG Agent, an expert educational assistant specialized in history.

Your task is to answer student questions based only on the provided context from study materials. Do NOT add any information that is not supported by the context.

Please follow these instructions carefully:
1. Provide a clear, accurate, and concise answer in 3 to 5 sentences.
2. Include key facts such as important dates, names, inventions, and their impacts where relevant.
3. If the context is incomplete or does not contain enough information to answer fully, politely state that the information is insufficient.
4. Use simple and clear language suitable for high school students.
5. Organize your answer logically, and use bullet points if multiple items need listing.
6. Avoid speculation or unrelated information.

---

[Examples omitted for brevity]

---

Now, please answer the following question based on the context provided.

When providing the answer, please structure it clearly and professionally. Use bullet points to list key facts or items, and include tables if appropriate to organize comparative or numerical data. Ensure the explanation is detailed, logically organized, and easy to understand for high school students. Avoid overly long paragraphs; instead, break down complex information into digestible sections with headings or lists where relevant.

Please provide a detailed and comprehensive answer, including bullet points, tables if appropriate, and explanations. Aim for at least 6-10 sentences or more, covering all relevant aspects of the question based on the context.

Context:
{context}

Question:
{question}

Answer:"""

def generate_gemini_response(question: str, context: str) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating Gemini response: {str(e)}"

def load_questions(input_path: str, file_type: str):
    questions_data = []
    if file_type == "json":
        with open(input_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    elif file_type == "csv":
        df = pd.read_csv(input_path)
        for idx, row in df.iterrows():
            questions_data.append({
                "Id": row.get("Id") or row.get("id") or str(idx+1),
                "Question": row.get("Question") or row.get("question")
            })
    else:
        raise ValueError("Unsupported file type. Use 'json' or 'csv'.")
    return questions_data

def batch_answer_questions(input_path: str, output_csv: str, file_type: str, n_results: int = 5):
    questions_data = load_questions(input_path, file_type)
    output_rows = []

    for idx, item in enumerate(questions_data):
        q_id = item.get("Id") or item.get("id") or str(idx+1)
        question = item.get("Question") or item.get("question")
        if not question:
            print(f"Skipping entry {q_id}: No question found.")
            continue

        # Retrieve relevant chunks (documents + metadata)
        results = vdb.collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "metadatas"]
        )

        docs = results["documents"][0]
        metadatas = results.get("metadatas", [{}])[0]

        # Build combined context text
        context = "\n\n".join(docs)

        # Aggregate sections and pages from metadatas
        sections = set()
        pages = set()
        for meta in metadatas:
            if meta:
                secs = meta.get("sections") or meta.get("section")
                if secs:
                    if isinstance(secs, list):
                        sections.update(secs)
                    else:
                        sections.add(secs)
                pgs = meta.get("pages")
                if pgs:
                    if isinstance(pgs, list):
                        pages.update(pgs)
                    else:
                        pages.add(pgs)

        # Convert sets to sorted lists and then strings
        sections_str = ", ".join(sorted(sections)) if sections else ""
        pages_str = ", ".join(map(str, sorted(pages))) if pages else ""

        # Generate answer using Gemini
        answer = generate_gemini_response(question, context)

        output_rows.append({
            "Id": q_id,
            "Question": question,
            "Context": context,
            "Answer": answer,
            "Sections": sections_str,
            "Pages": pages_str
        })

        print(f"Processed Id {q_id}: {question[:50]}...")

    # Save to CSV
    df_out = pd.DataFrame(output_rows)
    df_out.to_csv(output_csv, index=False)
    print(f"\nAll answers saved to: {output_csv}")

if __name__ == "__main__":
    file_type = input("Enter input file type (json/csv): ").strip().lower()
    input_path = input("Enter the path to your input file: ").strip()
    output_name = input("Under what name do you want to save the output CSV file? (without extension): ").strip()
    output_csv_path = f"outputs/{output_name}.csv"
    batch_answer_questions(input_path, output_csv_path, file_type)
