# Future Minds Chatbot

## Overview

Future Minds Chatbot is an AI-powered educational assistant designed to enhance learning experiences through multiple specialized agents. The system leverages modern natural language processing techniques, including retrieval-augmented generation (RAG), to provide accurate and contextually relevant responses to user queries.

## Features

### History Question Answering

The History Agent uses RAG technology to answer questions based on textbook content. It:

- Processes and indexes PDF textbooks
- Retrieves relevant context for user questions
- Generates accurate answers with source citations
- Provides section and page references

### Language Translation

The Translator Agent supports translation between multiple languages including:

- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean, Chinese
- Arabic, Hindi, Bengali, Sinhala, Tamil

### Text Summarization

The Summarizer Agent condenses long texts into concise summaries with adjustable length settings.

### Study Planning

The Planner Agent helps create structured study plans with:

- Goal-oriented planning
- Deadline management
- Resource allocation

### Task Management

The Todo Agent provides a simple yet effective task management system with:

- Task creation with priorities
- Due date tracking
- Task completion status

## Project Structure

```
├── agents/                  # AI agent implementations
│   ├── history_agent.py     # RAG-based history Q&A agent
│   ├── translator_agent.py  # Multi-language translation agent
│   ├── summarizer_agent.py  # Text summarization agent
│   ├── planner_agent.py     # Study planning agent
│   └── todo_agent.py        # Task management agent
├── data/                    # Source data files
│   └── textbook.pdf         # Source textbook for history agent
├── processed_data/          # Processed and indexed data
│   └── chroma_db/           # Vector database for RAG
├── src/                     # Core functionality modules
│   ├── pdf_processing.py    # PDF extraction and processing
│   ├── embendding_vectordb.py # Vector embedding utilities
│   └── query_module.py      # Query processing module
├── static/                  # Web application static assets
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── templates/               # HTML templates for web interface
├── app.py                   # Flask web application
└── main.py                  # Command-line interface
```

## Technology Stack

- **Backend**: Python, Flask
- **Database**: ChromaDB (vector database)
- **AI Models**: Google Gemini, SentenceTransformer
- **PDF Processing**: PDFPlumber
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository

   ```
   git clone https://github.com/yourusername/future-minds-chatbot.git
   cd future-minds-chatbot
   ```

2. Install dependencies

   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables
   Create a `.env` file in the project root with the following:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Usage

#### Web Interface

Start the Flask web server:

```
python app.py
```

Access the web interface at http://localhost:5000

#### Command Line Interface

For direct interaction with the history agent:

```
python main.py
```

## Data Processing

To process a new textbook for the history agent:

1. Place the PDF file in the `data/` directory
2. Run the processing script:
   ```
   python -m src.pdf_processing
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was developed as part of the Future Minds educational initiative
- Special thanks to all contributors and educational partners
