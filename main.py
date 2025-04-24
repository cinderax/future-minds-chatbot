import os
import sys
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

sys.path.append("src")
from src.query_module import HistoryQuestionAnswerer

CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "processed_data/chroma_db")

def verify_collection(client, collection_name):
    try:
        collection = client.get_collection(collection_name)
        return {
            "exists": True,
            "collection_object": collection,
            "name": collection.name,
            "id": collection.id,
            "count": collection.count()
        }
    except Exception as e:
        available = client.list_collections()
        return {
            "exists": False,
            "error": str(e),
            "available_collections": available
        }

def main():
    load_dotenv()

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not set in environment.")
        return

    collection_name = input("Enter the ChromaDB collection name to use: ").strip()
    if not collection_name:
        print("No collection name provided. Exiting.")
        return

    try:
        # Create and share a single PersistentClient instance
        client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(allow_reset=True, is_persistent=True)
        )
    except Exception as e:
        print(f"Failed to initialize ChromaDB client: {e}")
        return

    verification = verify_collection(client, collection_name)
    if not verification["exists"]:
        print(f"Collection '{collection_name}' not found.")
        print("Available collections:")
        for c in verification.get("available_collections", []):
            print(f" - {c}")
        return

    try:
        # Pass the shared client instance to HistoryQuestionAnswerer
        answerer = HistoryQuestionAnswerer(client=client, collection_name=collection_name)
    except Exception as e:
        print(f"Failed to initialize HistoryQuestionAnswerer: {e}")
        return

    print("\n=== History Question Answering System ===")
    print("Type 'exit' or 'quit' to end the session\n")

    while True:
        try:
            question = input("Enter your history question: ").strip()
            if question.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not question:
                continue

            print("Analyzing question...")
            result = answerer.answer_question(question)

            print("\n=== Answer ===")
            print(result.get("answer", "No answer generated"))

            print("\n=== References ===")
            print(f"Sections: {result.get('sections', 'N/A')}")
            print(f"Pages: {result.get('pages', 'N/A')}")

            print("\n--- Context Preview ---")
            context = result.get("context", "")
            preview = (context[:250] + "...") if len(context) > 250 else context
            print(preview)

        except Exception as e:
            print(f"Error processing question: {e}")

if __name__ == "__main__":
    main()
