# 🔧 Project Plan: History-Aware AI Chatbot (Ravi's RAG Bot)

## 1. Objective
Build an intelligent chatbot that can:
- Answer Grade 11 History questions from a textbook PDF.
- Use Retrieval-Augmented Generation (RAG) with Gemini-1.5-Flash.
- Retrieve relevant context from the textbook using a vector database (ChromaDB).
- Generate accurate answers along with correct section and page references.

## 2. Key Components

### ✅ Input Files
- `textbook.pdf`: Source material for answering questions.
- `queries.json`: JSON file with questions to answer.

### ✅ Output File
- `submission.csv` with columns:
  ```
  ID, Context, Answer, Sections, Pages
  ```

## 3. Architecture Overview
```
PDF ➜ Chunker ➜ Embedder ➜ ChromaDB
                             ⬇
          Query ➜ Retriever ➜ Gemini ➜ Answer
                                     ⬇
                                CSV Writer
```

## 4. Tools & Stack
- **Language**: Python 3
- **Embedding Model**: `all-mpnet-base-v2` (via SentenceTransformers)
- **Vector Store**: ChromaDB
- **LLM**: `gemini-1.5-flash`
- **Other Libraries**: `nltk`, `pdfplumber`, `pandas`, `fastapi` (optional), `google.generativeai`

## 5. Module Breakdown

### 🧩 `pdf_chunker.py`
- Input: PDF
- Output: Sentence-based chunks with metadata (section, page)

### 🧠 `vector_db.py`
- Embeds and stores chunks using ChromaDB
- Handles similarity search on questions

### 💬 `gemini_wrapper.py`
- Wraps Gemini-1.5-Flash API
- Accepts a question + context, returns an answer

### 🔁 `run_pipeline.py` *(NEW)*
- Loads `queries.json`
- For each query:
  - Retrieves relevant context
  - Generates answer using Gemini
  - Records section and page references
- Outputs final `submission.csv`

### 🖥️ `main.py` *(Optional)*
- FastAPI app for interactive use/testing
- Not used for competition submission

## 6. Workflow
1. Run `pdf_chunker.py` on textbook PDF → get `chunks.csv`
2. Run `vector_db.py` to embed and store vectors in ChromaDB
3. Run `run_pipeline.py` on `queries.json` to generate `submission.csv`
4. Submit CSV via competition portal

## 7. Compliance Checklist
- ✅ Only uses `gemini-1.5-flash`
- ✅ No external data or models
- ✅ Output format matches submission requirements
- ✅ Reproducible pipeline in Python

## 8. Stretch Goals (Optional)
- Agent-based planner to route different types of queries
- Context summarizer before Gemini input
- Confidence scorer / ranking system
- Add translator or sentiment analyzer agent

## 9. GitHub Deliverables
- Code repo with:
  - `README.md`
  - All scripts and requirements.txt
  - Sample inputs/outputs
- `submission.csv`
- Optional: video demo

---
Ready to execute. Let’s finish this strong. 🚀
