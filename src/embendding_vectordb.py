import json
import chromadb
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddingFunction:
    def __init__(self, model_name="all-mpnet-base-v2", device="cpu"):
        self.model = SentenceTransformer(model_name, device=device)

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input)
        return embeddings.tolist()


# ... [Keep all previous imports and classes] ...

def create_chroma_db(json_file_path, collection_name):
    # Load JSON file and validate
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks_data = data.get("chunks", [])
        if not chunks_data:
            print("Error: No 'chunks' key or empty list in JSON")
            return None
    except Exception as e:
        print(f"Error loading JSON: {str(e)}")
        return None

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="processed_data/chroma_db")

    # Delete existing collection if present
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception as e:
        print(f"No existing collection to delete: {str(e)}")

    # Create collection with proper name
    embedding_function = SentenceTransformerEmbeddingFunction()
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    # Prepare documents, metadatas, and IDs
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks_data):
        if isinstance(chunk, str) and chunk.strip():
            documents.append(chunk.strip())
            metadatas.append({"source": "your_source_here"})
            ids.append(f"doc_{i}")

    if not documents:
        print("No valid documents to add.")
        return None

    # Batch add documents
    batch_size = 100
    for batch_idx in range(0, len(documents), batch_size):
        batch_end = batch_idx + batch_size
        collection.add(
            documents=documents[batch_idx:batch_end],
            metadatas=metadatas[batch_idx:batch_end],
            ids=ids[batch_idx:batch_end]
        )
        print(f"Added batch {batch_idx//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

    print(f"Created collection '{collection.name}' with {len(documents)} items")
    return collection

if __name__ == "__main__":
    json_file_path = input("JSON file path: ").strip()
    collection_name = input("Collection name: ").strip()
    
    collection = create_chroma_db(json_file_path, collection_name)
    
    if collection:
        # Verify collection name matches input
        print(f"\nVerification:")
        print(f"Requested name: {collection_name}")
        print(f"Actual name:    {collection.name}")
        print(f"Count:          {len(collection.get()['ids'])} items")
        
        # Check through client listing
        client = chromadb.PersistentClient(path="processed_data/chroma_db")
        collections = client.list_collections()
        print("\nAll collections:")
        for col in collections:
            print(f"- {col.name} (ID: {col.id})")
