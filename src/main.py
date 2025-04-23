import os
import sys
from dotenv import load_dotenv
from vector_db import VectorDB
import google.generativeai as genai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.summarizer import SummarizerAgent  # <-- Import summarizer

# --- Load environment variables securely ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY not set. Please add it to your .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

vdb = VectorDB(csv_path="outputs/chunks.csv")  # Adjust path as needed
summarizer = SummarizerAgent()  # <-- Initialize summarizer

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

def process_question(question: str, summary: bool = False):
    print("\nProcessing the question...")
    retrieved_chunks = vdb.query(question, n_results=5)
    if not retrieved_chunks or all(not c.strip() for c in retrieved_chunks):
        print("No relevant context found for your question. Please try rephrasing.")
        return

    context = "\n".join(retrieved_chunks)
    detailed_answer = generate_gemini_response(question, context)
    
    print("\n--- Context Used ---")
    print(context)
    print("\n--- Full Answer ---")
    print(detailed_answer)
    
    if summary:
        summary_answer = summarizer.summarize(detailed_answer)
        print("\n--- Summary ---")
        print(summary_answer)

if __name__ == "__main__":
    print("FutureMinds chatbot is ready. Ask a question (type 'exit' to quit).")
    while True:
        question = input("\nYour question: ")
        if question.lower() == 'exit':
            print("\nExiting chatbot...")
            break
        want_summary = input("Do you want a summary? (y/n): ").lower() == 'y'
        process_question(question, summary=want_summary)
