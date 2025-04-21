# AI-Powered History Textbook Chatbot

This project is an AI-powered chatbot designed to answer academic queries about a Grade 11 History textbook using a Retrieval-Augmented Generation (RAG) approach. It leverages ChromaDB for efficient vector storage and similarity search, and the Gemini-1.5-Flash model to generate context-aware answers.

## Features

- **Query Answering**: Answer questions based on a PDF textbook using the Gemini-1.5-Flash model.
- **Advanced Agents**: Includes multiple agents for query routing, context summarization, confidence ranking, and more.
- **PDF Processing**: The system chunks the textbook into smaller, manageable pieces and stores them as vectors for fast retrieval.
- **ChromaDB**: Uses ChromaDB as the vector database to store embeddings and perform similarity searches.

## Project Structure

/your-chatbot-repo
│
├── README.md                   # Project overview and setup instructions
├── requirements.txt            # Dependencies for the project
├── main.py                     # (Optional) FastAPI app for interactive use/testing
├── run_pipeline.py             # Core pipeline: loads queries, retrieves context, calls Gemini, and writes CSV
├── pdf_chunker.py              # PDF chunking script
├── vector_db.py                # Script to embed chunks and store vectors (ChromaDB)
├── gemini_wrapper.py           # Wrapper for Gemini-1.5-Flash API
│
├── agents/                     # Folder for the advanced agents
│   ├── query_planner.py        # Query-type planning agent
│   ├── context_summarizer.py   # Context summarizer agent
│   ├── confidence_ranker.py    # Answer confidence scorer/ranker
│   ├── translator.py           # (Optional) Translator agent
│   ├── sentiment_analyzer.py   # (Optional) Sentiment analyzer agent
│
├── data/                       # Folder to store data files
│   ├── queries.json            # The test queries for the competition
│   ├── textbook.pdf            # The source textbook PDF
│   └── chunks.csv              # Chunked and processed PDF data
│
├── outputs/                    # Folder for outputs
│   ├── submission.csv          # Final output for competition submission
│   └── logs/                   # Logs for debugging, if any
│
└── .gitignore                  # Files/folders to ignore in version control

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2.	Install dependencies:

	```
	pip install -r requirements.txt
	```


Usage

To process a set of queries and generate the final CSV, run the pipeline:

python run_pipeline.py

Optional: For Interactive Use

If you’d like to interact with the system via a FastAPI app (for local testing), you can run:

python main.py

Dependencies
	•	chromadb for vector storage and retrieval
	•	gemini-1.5-flash for the question-answering model
	•	pandas for handling CSV output
	•	nltk, pdfplumber, and others for text chunking and PDF processing

License

This project is licensed under the MIT License - see the LICENSE file for details.

---

### What's Covered Here:
- **Overview**: Explains what the chatbot does and the tech stack.
- **Project Structure**: A breakdown of the repo, like we discussed earlier.
- **Installation**: Basic setup instructions for the repo.
- **Usage**: How to run the core pipeline and optional interactive testing.
- **Dependencies**: A list of major dependencies.
- **License**: You can adjust or add licensing info as needed.

---

Let me know if we should add any specific details or if you're ready to move on to the next part of the setup!