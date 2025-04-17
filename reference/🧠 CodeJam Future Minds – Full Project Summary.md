
## 🔥 TL;DR

Build a **multi-agent chatbot** that reads and understands a **Grade 11 History textbook** and answers queries using **Gemini 1.5 Flash**, a **vector DB**, and at minimum, a **RAG (Retrieval-Augmented Generation) agent**. Judging is based on accuracy, relevance, references, and innovation. Deliver a working solution, demo video, and well-structured code or Langflow pipeline.

---

## ✅ WHAT TO DO

### 🔧 Build Core System
- Create a **Multi-Agent Chatbot**
  - **Mandatory**: A RAG Agent (Retrieve relevant text + Generate answers)
  - **Optional (recommended)**: Add agents like Summarizer, Task Planner, Translator, etc.

### 🧠 Tech Requirements
- Use ONLY **Gemini 1.5 Flash** (via Google AI API)
- Use a **vector database** for similarity search (FAISS, Chroma, Pinecone, etc.)

### 📦 Dataset
- `queries.json`: Query ID, context, answer, references
- Textbook PDF: For embedding and retrieval
- Sample submission file provided

### 📤 Submission Requirements
1. CSV File (`ID, Context, Answer, Sections, Pages`)
2. Langflow JSON (if Langflow is used)
3. GitHub Repo link (if coding manually)
4. Demo Video (≤15 min): Must show answer generation and workflow
5. (Optional) Extra code/assets

### 🧪 Evaluation Criteria
| Criteria              | Weight |
|----------------------|--------|
| Answer Correctness   | 40%    |
| Context Precision    | 20%    |
| Answer Faithfulness  | 20%    |
| Reference Accuracy   | 10%    |
| Innovation           | 10%    |

---

## ❌ WHAT NOT TO DO
- ❗ Don’t use any model except **Gemini 1.5 Flash**
- ❗ Don’t use paid or private resources
- ❗ Don’t miss required columns/formats
- ❗ Don’t submit unreproducible code or workflows
- ❗ Don’t try to cheat—top teams face live Q&A

---

## 🧰 Resources
- [Get Gemini API Key](https://aistudio.google.com/u/2/apikey)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Langflow Docs](https://docs.langflow.org/concepts-flows)
- [RAG Tutorial](https://youtu.be/2TJxpyO3ei4)
- [Langflow + RAG Example](https://youtu.be/QmUsG_3wHPg)
- [AI Agents 101](https://cloud.google.com/discover/what-are-ai-agents)

---

## 🤔 Code vs Langflow – Which One Should You Choose?

### 🚀 Use **Code** If:
- You want full control, flexibility, and optimization
- You’re comfortable with Python
- You're aiming for a top-tier performance and innovation

### 🧩 Use **Langflow** If:
- You're short on time or new to coding
- You want to prototype visually with no-code tools
- You only aim to submit a valid, working demo

### ⚖️ Quick Comparison

| Goal                          | Recommendation |
|------------------------------|----------------|
| Just want a working solution | **Langflow**   |
| Want to compete seriously    | **Code it**    |
| Want to learn deeply         | **Code it**    |
| Hate debugging               | **Langflow**   |
| Max evaluation score         | **Code it**    |

### 💡 Pro Strategy
Start with Langflow to prototype, then **convert to Python** for full control and a polished solution.

---

## 🧭 Suggested Dev Workflow (if coding)
1. Parse textbook PDF and chunk the content
2. Store embeddings in vector DB (e.g., FAISS)
3. RAG Agent: Retrieve relevant chunks and prompt Gemini for answers
4. Add extra agents (summarizer, translator, etc.)
5. Build Langflow JSON or GitHub repo for submission
6. Create UI for demo (CLI, Flask, or Streamlit)

---

---

## 📁 Folder Structure

```
future-minds-chatbot/
├── data/
│   ├── textbook.pdf
│   └── queries.json
├── embeddings/
│   └── faiss_index/
├── agents/
│   ├── rag_agent.py
│   ├── planner_agent.py
│   ├── summarizer_agent.py
│   └── reference_mapper.py
├── utils/
│   ├── pdf_parser.py
│   ├── embedding_utils.py
│   ├── retrieval_utils.py
│   └── prompt_templates.py
├── app/
│   ├── main.py
│   └── interface.py
├── outputs/
│   ├── answers.csv
│   └── logs/
├── README.md
├── requirements.txt
└── .env  # Gemini API key
```

---

## 🚀 Step-by-Step Build Path

### ✅ STEP 1: Textbook Parsing & Chunking

> `utils/pdf_parser.py`

- Use `pdfplumber` or `PyMuPDF`
- Chunk the book by headers/subsections
- Add metadata: `section`, `page`
- Output: list of {text, section, page}

### ✅ STEP 2: Embedding + Vector DB

> `utils/embedding_utils.py`

- Use `sentence-transformers` or Gemini’s embedding model
- Store vectors in **FAISS** index
- Save metadata: `section`, `page`, `chunk_id`

### ✅ STEP 3: Retrieval Logic

> `utils/retrieval_utils.py`

- Given a query, embed it
- Retrieve top-k most similar vectors using FAISS
- Return matching chunks and metadata

### ✅ STEP 4: RAG Agent

> `agents/rag_agent.py`

- Receive a query
- Call `retrieval_utils.py` to get top chunks
- Format prompt with chunks (few-shot if needed)
- Use Gemini 1.5 Flash API
- Return: `answer`, `context`, `section_refs`, `pages`

### ✅ STEP 5: Planner Agent

> `agents/planner_agent.py`

- Input: query
- Output: list of subqueries (if compound)
- Use Gemini or rule-based logic

### ✅ STEP 6: Summarizer Agent

> `agents/summarizer_agent.py`

- Input: list of long context chunks
- Output: summarized version under token limit

### ✅ STEP 7: Reference Mapper Agent

> `agents/reference_mapper.py`

- Input: context chunks
- Output: list of `section`, `page` pairs
- Ensures citation traceability

### ✅ STEP 8: Main Pipeline

> `app/main.py`

- Load FAISS, initialize all agents
- Read `queries.json`
- For each query:
  - Pass to `planner_agent`
  - Each subquery goes through `rag_agent`
  - Use `reference_mapper` to fetch references
- Output: Format to `answers.csv`

### ✅ STEP 9: Interface (Optional)

> `app/interface.py`

- Build with Streamlit or Flask
- Input: user query
- Output: chatbot answer + context + references

---

## 🧪 Evaluation Cheatsheet

| Metric             | Strategy                                                    |
|-------------------|-------------------------------------------------------------|
| Answer Correctness| Use high-quality prompts, test multiple variants            |
| Context Precision | Chunk smartly, filter garbage, rerank with hybrid search    |
| Faithfulness      | Force model to “stick to” retrieved context only            |
| Reference Accuracy| Track metadata, map sections and pages properly             |
| Innovation        | Add planner, summarizer, reference agents. Show real flow.  |

---

## 📦 Final Deliverables Checklist

- [ ] `answers.csv` → formatted: ID, Context, Answer, Sections, Pages
- [ ] GitHub Repo → clean, documented, reproducible
- [ ] Demo Video ≤ 15 min → walkthrough + live demo
- [ ] (Optional) Langflow JSON if used
- [ ] README with setup instructions

---

## 🔑 Requirements.txt (Starter)
```txt
faiss-cpu
PyMuPDF
sentence-transformers
openai
pandas
python-dotenv
streamlit
flask
```
Add `google.generativeai` if using Gemini official SDK.

---
