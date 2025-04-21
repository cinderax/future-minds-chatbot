# FutureMinds Chatbot


- An AI-powered educational assistant designed to answer student-level questions based on grade 11 History textbook content.  
- This project uses custom PDF chunking, ChromaDB for vector storage, and Google Gemini for answer generation, creating a robust Retrieval-Augmented Generation (RAG) pipeline.

---

## Features

- Extracts text chunks from PDFs using `pdfplumber` and `nltk` sentence tokenization.
- Converts chunks into vector embeddings using open-source Sentence Transformers.
- Stores embeddings in ChromaDB for fast semantic search.
- Integrates with Google Gemini API to generate precise, context-aware answers.
- Supports batch question answering and interactive web interface (Flask).
- Fully modular and easy to extend.

---

## Project Structure

```
FutureMinds-Chatbot/
│
├── data/
│   ├── chunks.csv
│   ├── chunks.json
│   └── textbook.pdf
│
├── src/
│   ├──chroma_db
│   ├── app.py
│   ├── batch_answer_generator.py
│   ├── chunker.py
│   └── vector_db.py
|   |__ main.py
│
├── README.md
├── requirements.txt
│
│
├── templates/
│   └── index.html
│
```

---

## Setup Instructions

### 1. Clone the repository

```
https://github.com/cinderax/future-minds-chatbot.git
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Set up API keys

Create a `.env` file in the root directory containing:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Load environment variables in your scripts using `python-dotenv` or your preferred method.

### 4. Prepare data

- Place your PDF textbooks in the `data/`  with name `teaxtbook.pdf`  folder.
- Run `chunk_pdf.py` to extract chunks and save as `chunks.csv`.

### 5. Build vector database

- Use `vector_db.py` to load `chunks.csv` into ChromaDB and generate embeddings.

### 6. Run batch answering

```
python batch_answer_generator.py
```

This will read questions from `Future-Minds-Sample-Submission.csv`, generate answers, and save them to `Future-Minds-Submission-Answers.csv`.

### 7. (Optional) Run web app

```
python app.py
```

Open your browser at `http://127.0.0.1:5000` to interact with the chatbot.

---

## Usage

### Batch answering script

```
python batch_answer_generator.py
```

### Interactive chatbot (Flask)

```
python app.py
```

---

## Dependencies

- Python 3.8+
- [pandas](https://pandas.pydata.org/)
- [chromadb](https://github.com/chroma-core/chroma)
- [sentence-transformers](https://www.sbert.net/)
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [flask](https://flask.palletsprojects.com/)
- [nltk](https://www.nltk.org/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [python-dotenv](https://pypi.org/project/python-dotenv/)


---

## Contact

For questions or collaboration, reach out at cinderax@icloud.com

---
