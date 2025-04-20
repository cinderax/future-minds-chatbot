import faiss
from sentence_transformers import SentenceTransformer
import pickle
import warnings
import os
from typing import List, Dict, Any, Optional

class FaissVectorStore:
    def __init__(
        self,
        embedding_model_name: str = 'all-mpnet-base-v2',
        dim: int = 768,
        faiss_index_type: str = "HNSW",  # Use HNSW for better memory handling
        use_gpu: bool = False,
        max_threads: int = 1  # Limit number of threads used by PyTorch
    ):
        # Set environment variable to limit the number of threads used by PyTorch
        os.environ["OMP_NUM_THREADS"] = str(max_threads)
        os.environ["MKL_NUM_THREADS"] = str(max_threads)
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU for PyTorch (use if needed)

        self.embedder = SentenceTransformer(embedding_model_name, device='cpu')  # No threads argument
        self.dim = dim
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self._init_index(faiss_index_type, use_gpu)

    def _init_index(self, index_type: str, use_gpu: bool):
        """Initialize FAISS index with different configurations"""
        if index_type == "Flat":
            self.index = faiss.IndexFlatIP(self.dim)
        elif index_type == "HNSW":
            # Use HNSW for approximate search with better memory efficiency
            self.index = faiss.IndexHNSWFlat(self.dim, 32)  # 32 is the number of neighbors to search for
        elif index_type == "IVF":
            # Requires training
            quantizer = faiss.IndexFlatIP(self.dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.dim, 100)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")

        if use_gpu:
            self._move_to_gpu()

    def _move_to_gpu(self):
        try:
            res = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
        except Exception as e:
            warnings.warn(f"GPU acceleration failed: {str(e)}")

    def add_chunks(self, chunks: List[Dict], batch_size: int = 64):
        """Add chunks with batch processing and validation"""
        if not chunks:
            return

        # Validate chunks
        valid_chunks = [
            chunk for chunk in chunks
            if isinstance(chunk, dict) and "text" in chunk and len(chunk["text"]) > 0
        ]
        
        # Batch processing
        for i in range(0, len(valid_chunks), batch_size):
            batch = valid_chunks[i:i+batch_size]
            texts = [chunk["text"] for chunk in batch]
            
            try:
                embeddings = self.embedder.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    normalize_embeddings=True  # Directly get normalized vectors
                )
            except Exception as e:
                warnings.warn(f"Failed to encode batch {i}: {str(e)}")
                continue

            if isinstance(self.index, faiss.IndexIVFFlat):
                if not self.index.is_trained:
                    # Train IVF index
                    self.index.train(embeddings)
                
            self.index.add(embeddings)
            self.texts.extend(texts)
            self.metadatas.extend([
                {k: v for k, v in chunk.items() if k != "text"}
                for chunk in batch
            ])

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search with optional metadata filtering"""
        try:
            query_embedding = self.embedder.encode(
                [query_text],
                convert_to_numpy=True,
                normalize_embeddings=True
            )
        except Exception as e:
            warnings.warn(f"Query encoding failed: {str(e)}")
            return []

        # Search FAISS
        distances, indices = self.index.search(query_embedding, top_k * 2)  # Oversample for filtering

        # Filter and process results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.texts):
                continue

            metadata = self.metadatas[idx]
            if metadata_filter and not all(
                metadata.get(k) == v for k, v in metadata_filter.items()
            ):
                continue

            results.append({
                "text": self.texts[idx],
                "metadata": metadata,
                "score": float(dist)
            })

            if len(results) >= top_k:
                break

        return results

    def save(self, path_prefix: str):
        """Save index and metadata with versioning"""
        index_path = f"{path_prefix}.index"
        metadata_path = f"{path_prefix}.metadata.pkl"
        
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump({s
                "texts": self.texts,
                "metadatas": self.metadatas,
                "config": {
                    "dim": self.dim,
                    "embedding_model": self.embedder.__class__.__name__  # Save the model class name
                }
            }, f)

    @classmethod
    def load(cls, path_prefix: str, use_gpu: bool = False):
        """Factory method for loading"""
        index_path = f"{path_prefix}.index"
        metadata_path = f"{path_prefix}.metadata.pkl"
        
        instance = cls.__new__(cls)
        instance.index = faiss.read_index(index_path)
        
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            instance.texts = data["texts"]
            instance.metadatas = data["metadatas"]
            instance.dim = data["config"]["dim"]
            instance.embedder = SentenceTransformer(data["config"]["embedding_model"])
        
        if use_gpu:
            instance._move_to_gpu()
            
        return instance

    def __len__(self):
        return len(self.texts)