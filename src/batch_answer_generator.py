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

Example 1:
Context:
"There are so many coal mines in Britain. South Wales, Yorkshire, Lancashire are some places where coal mines are situated... Thomas Newcomen invented a steam engine in 1735 to pump water... James Watt developed this to a new steam engine in 1736... Humphry Davy produced the safety lamp in 1812... In 1839, a method was found to take coal out of the mines using iron cables instead of copper."

Question:
What were the key developments in the coal industry during the Industrial Revolution?

Answer:
Key developments in the coal industry during the Industrial Revolution included the invention of steam engines by Thomas Newcomen and improvements by James Watt, which helped pump water out of mines. Humphry Davy's safety lamp improved miner safety, and the introduction of iron cables in 1839 enhanced coal extraction. These innovations greatly increased mining efficiency and safety.

---

Example 2:
Context:
"British people came to Sri Lanka and started mega scale cultivations. Many factories were started in connection to thus started cultivations such as tea, coconut, rubber and machines were imported from Britain to be used in those factories. Roads and railways were introduced... the Colombo–Kandy road was constructed... railway was started in 1858... postal system in 1815."

Question:
How did the Industrial Revolution affect Sri Lanka?

Answer:
The Industrial Revolution affected Sri Lanka by introducing large-scale plantation agriculture for crops like tea, coconut, and rubber. The British established factories and imported machinery to process these crops. Infrastructure such as roads, railways, and postal services was developed to support the plantations, leading to social and economic changes.

---
You are a knowledgeable and approachable history teacher. If the student greets you or thanks you, respond warmly as a real teacher would.

If the user gives input like “clear”, or if the system provides mismatched or confusing context, take a moment to think before answering. Remember, the user expects to be interacting with a real human—mistakes can happen.

If you can’t understand the question, kindly ask the student to submit it again.
---

Now, please answer the following question based on the context provided.

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

def batch_answer_questions_from_json(input_json: str, output_csv: str, n_results: int = 5):
    # Load questions from JSON file
    with open(input_json, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)

    # Prepare list for output rows
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
    input_json_path = "data/questions.json"  # Path to your questions JSON file
    output_csv_path = "outputs/answers_output.csv"  # Desired output CSV path
    batch_answer_questions_from_json(input_json_path, output_csv_path)
