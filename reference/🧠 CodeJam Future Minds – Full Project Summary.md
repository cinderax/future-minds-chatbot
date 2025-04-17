
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

**Need help with architecture, code, or prompts? I’ve got your back.**
