# 🤖 Future Minds Chatbot

## 🧠 Overview

**Future Minds Chatbot** is an AI-powered educational assistant designed to enhance learning through a suite of intelligent agents. It leverages modern NLP techniques—including **hybrid retrieval-augmented generation (RAG)**—to deliver accurate, contextual, and helpful responses.

---

## ✨ Features

### 📚 History Question Answering

The **History Agent** uses a **hybrid RAG approach** combining:

- 📄 **Offline context**: From processed and indexed PDF textbooks
- 🌐 **Online context**: From approved educational websites

This two-tiered method delivers rich, citation-backed answers—even when the source textbook is limited.

✅ Key capabilities:
- Relevant context retrieval  
- Accurate answer generation with citations  
- Section and page reference support  

---

### 🌍 Language Translation

The **Translator Agent** supports multilingual translation across:

🇬🇧 English | 🇪🇸 Spanish | 🇫🇷 French | 🇩🇪 German | 🇮🇹 Italian | 🇵🇹 Portuguese  
🇷🇺 Russian | 🇯🇵 Japanese | 🇰🇷 Korean | 🇨🇳 Chinese | 🇸🇦 Arabic  
🇮🇳 Hindi | 🇧🇩 Bengali | 🇱🇰 Sinhala | 🇮🇳 Tamil  

---

### 📝 Text Summarization

The **Summarizer Agent** condenses lengthy texts into clear, concise summaries.

- 🧾 Adjustable length settings  
- 📌 Highlights key points

---

### 📆 Study Planning

The **Planner Agent** creates structured, goal-driven study plans:

- 🎯 Goal tracking  
- ⏰ Deadline management  
- 📚 Resource allocation  

---

### ✅ Task Management

The **Todo Agent** simplifies your workflow:

- 🗂️ Task creation with priorities  
- 🗓️ Due date tracking  
- ✔️ Completion status updates  

---

## 🗂️ Project Structure

```
├── agents/                      # 🤖 AI agent implementations
│   ├── __init__.py
│   ├── history_agent.py
│   ├── planner_agent.py
│   ├── summarizer_agent.py
│   ├── todo_agent.py
│   └── translator_agent.py
├── data/                        # 📄 Raw input textbook
│   └── textbook.pdf
├── processed_data/              # 🧠 Vector DB data
│   └── chroma_db/
├── src/                         # 🛠️ Core functionality
│   ├── __init__.py
│   ├── batch_answer_genarator.py
│   ├── collection_names.py
│   ├── embending_vectordb.py
│   ├── pdf_processing.py
│   └── query_module.py
├── static/                      # 🎨 Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── templates/                   # 🖼️ HTML templates
│   ├── base.html
│   ├── history.html
│   ├── index.html
│   ├── planner.html
│   ├── summarizer.html
│   ├── todo.html
│   └── translator.html
├── .gitignore                   # ❌ Git exclusions
├── app.py                       # 🚀 Flask web app
├── main.py                      # 🧪 CLI entry point
├── README.md                    # 📘 Project docs
├── requirements.txt             # 📦 Python dependencies
```

---

## ⚙️ Technology Stack

- **Backend**: 🐍 Python, Flask  
- **Database**: 🧬 ChromaDB (vector DB)  
- **AI Models**: 🧠 Google Gemini, SentenceTransformer  
- **PDF Processing**: 📄 PDFPlumber  
- **Frontend**: 🌐 HTML, CSS, JavaScript  

---

## 🚀 Setup Instructions

### 🔧 Prerequisites

- Python ≥ 3.8  
- pip (Python package manager)

---

### 📥 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/future-minds-chatbot.git
   cd future-minds-chatbot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

---

## 💡 Usage

### 🌐 Web Interface

Start the Flask server:

```bash
python app.py
```

Then visit [http://localhost:5000](http://localhost:5000)

---

### 🧪 Command Line Interface

Run the chatbot directly:

```bash
python main.py
```

---

### 📘 Process a New Textbook

1. Drop the PDF into the `data/` directory  
2. Run:

```bash
python -m src.pdf_processing
```

---

## 🙌 Acknowledgments

- Developed as part of the **Future Minds** educational initiative  
- Huge thanks to our contributors and educational partners 💙

