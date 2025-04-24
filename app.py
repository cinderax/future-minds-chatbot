from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
import sys

sys.path.append("src")
from src.query_module import HistoryQuestionAnswerer

# Load environment variables
load_dotenv()

app = FastAPI()

CHROMA_DB_PATH = "processed_data/chroma_db"
COLLECTION_NAME = "textbook"  # fixed collection name as requested

# Initialize Chroma client once
try:
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(allow_reset=True, is_persistent=True),
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize ChromaDB client: {e}")

# Verify collection exists
try:
    collection = client.get_collection(COLLECTION_NAME)
except Exception:
    available = client.list_collections()
    raise RuntimeError(f"Collection '{COLLECTION_NAME}' not found. Available collections: {available}")

# Initialize the answerer with shared client and fixed collection name
answerer = HistoryQuestionAnswerer(client=client, collection_name=COLLECTION_NAME)

# Define request and response models
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sections: list[str]
    pages: list[str]
    context_preview: str

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answerer.answer_question(question)
        context = result.get("context", "")
        preview = (context[:250] + "...") if len(context) > 250 else context

        return AnswerResponse(
            answer=result.get("answer", "No answer generated"),
            sections=result.get("sections", []),
            pages=result.get("pages", []),
            context_preview=preview,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")
#uvicorn app:app --reload