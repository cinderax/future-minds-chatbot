import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional

class VectorDB:
    def __init__(self, csv_path: str, persist_dir: str = "chroma_db", 
                 model_name: str = "all-mpnet-base-v2",
                 id_column: Optional[str] = "id", text_column: str = "text",
                 embedding_function=None):
        """
        Initialize vector database with persistent storage
        
        Args:
            csv_path: Path to CSV file containing chunks
            persist_dir: Directory to store ChromaDB data
            model_name: Sentence Transformer model name
            id_column: Name of the ID column in CSV (None to auto-generate)
            text_column: Name of the text content column in CSV
            embedding_function: Optional custom embedding function
        """
        self.csv_path = csv_path
        self.id_column = id_column
        self.text_column = text_column
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        if embedding_function:
            self.embedding_func = embedding_function
        else:
            self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )
        
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            embedding_function=self.embedding_func
        )
        
        if len(self.collection.get()['ids']) == 0:
            self._load_and_store_chunks()

    def _load_and_store_chunks(self, batch_size: int = 500):
        """Load chunks from CSV and store in ChromaDB"""
        try:
            df = pd.read_csv(self.csv_path)
            
            if self.text_column not in df.columns:
                raise ValueError(f"CSV missing text column: '{self.text_column}'")
            
            texts = df[self.text_column].tolist()
            if self.id_column is None or self.id_column not in df.columns:
                ids = [str(i) for i in range(len(df))]
            else:
                ids = df[self.id_column].astype(str).tolist()
            
            metadata_cols = [col for col in df.columns if col not in [self.id_column, self.text_column]]
            metadatas = df[metadata_cols].to_dict(orient='records') if metadata_cols else None
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size] if metadatas else None
                self.collection.add(
                    documents=batch_texts,
                    ids=batch_ids,
                    metadatas=batch_metadatas
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at: {self.csv_path}")

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """Query the vector database"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            print(f"Error during query: {e}")
            return []

    def reset_collection(self):
        """Delete and recreate the collection"""
        self.client.delete_collection(name="document_chunks")
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            embedding_function=self.embedding_func
        )
