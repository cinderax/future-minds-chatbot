import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List

class VectorDB:
    def __init__(self, csv_path: str, persist_dir: str = "chroma_db", 
                 model_name: str = "all-mpnet-base-v2",
                 id_column: str = "id", text_column: str = "text"):
        """
        Initialize vector database with persistent storage
        
        Args:
            csv_path: Path to CSV file containing chunks
            persist_dir: Directory to store ChromaDB data
            model_name: Sentence Transformer model name
            id_column: Name of the ID column in CSV (None to auto-generate)
            text_column: Name of the text content column in CSV
        """
        self.csv_path = csv_path
        self.id_column = id_column
        self.text_column = text_column
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Initialize embedding function
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            embedding_function=self.embedding_func
        )
        
        # Load data if collection is empty
        if len(self.collection.get()['ids']) == 0:
            self._load_and_store_chunks()

    def _load_and_store_chunks(self):
        """Load chunks from CSV and store in ChromaDB"""
        try:
            df = pd.read_csv(self.csv_path)
            
            # Validate text column exists
            if self.text_column not in df.columns:
                raise ValueError(f"CSV missing text column: '{self.text_column}'")
            
            # Get texts
            texts = df[self.text_column].tolist()
            
            # Generate IDs if column doesn't exist or None specified
            if self.id_column is None or self.id_column not in df.columns:
                ids = [str(i) for i in range(len(df))]  # Generate sequential IDs
            else:
                ids = df[self.id_column].astype(str).tolist()
            
            # Add to collection
            self.collection.add(
                documents=texts,
                ids=ids
            )
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at: {self.csv_path}")

    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """
        Query the vector database
        
        Args:
            query_text: Input query text
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0]
    
# if __name__ == "__main__":
#     db = VectorDB(csv_path="data/chunks.csv")
#     result = db.query("who is hitler?")
#     for i, doc in enumerate(result, 1):
#         print(f"[{i}] {doc}")