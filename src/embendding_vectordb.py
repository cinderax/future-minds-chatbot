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


def create_chroma_db(json_file_path, collection_name):
    # Load JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks_data = data.get("chunks", [])
    except FileNotFoundError:
        print(f"Error: File not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file_path}")
        return None

    # Initialize ChromaDB client with persistent path
    client = chromadb.PersistentClient(path="processed_data/chroma_db")

    # Delete existing collection if it exists
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except Exception:
        pass  # no collection to delete

    # Create collection with embedding function
    embedding_function = SentenceTransformerEmbeddingFunction()
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks_data):
        if isinstance(chunk, dict):
            text = chunk.get("text", "").strip()
            if not text:
                print(f"Skipping empty chunk at index {i}")
                continue

            metadata = {
                "source": "your_source_here",
                "page_number": chunk.get("page_number"),
                "section": chunk.get("section"),
                "subsection": chunk.get("subsection"),
                "chapter": chunk.get("chapter"),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index")
            }

            documents.append(text)
            metadatas.append(metadata)
            ids.append(f"doc_{i}")
        else:
            print(f"Skipping non-dict chunk at index {i}")

    if not documents:
        print("No valid chunks found to add to the collection.")
        return collection

    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        print(f"Added batch {i // batch_size + 1} / {(len(documents) + batch_size - 1) // batch_size}")

    print(f"Successfully created ChromaDB collection '{collection_name}' with {len(documents)} chunks")
    return collection


if __name__ == "__main__":
    json_file_path = input("Json file path: ").strip()
    collection_name = input("Collection Name: ").strip()

    collection = create_chroma_db(json_file_path, collection_name)

    if collection:
        print(f"Collection name: {collection.name}")
        results = collection.get()
        all_ids = results.get("ids", [])
        print(f"Collection '{collection_name}' contains {len(all_ids)} items.")
