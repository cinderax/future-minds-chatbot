import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables (optional if already loaded in main)
load_dotenv()

class SentenceTransformerEmbeddingFunction:
    def __init__(self, model_name="all-mpnet-base-v2", device="cpu"):
        self.model = SentenceTransformer(model_name, device=device)

    def __call__(self, input):  # must be named 'input'
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input)
        return embeddings.tolist()


class HistoryQuestionAnswerer:
    def __init__(self, client, collection_name="history_textbook", model_name="gemini-1.5-flash"):
        """
        Initialize with existing ChromaDB client and collection name.

        Args:
            client (chromadb.PersistentClient): Shared ChromaDB client instance.
            collection_name (str): Name of the ChromaDB collection.
            model_name (str): Gemini model name.
        """
        self.client = client

        self.embedding_function = SentenceTransformerEmbeddingFunction()

        self.collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=google_api_key)

        self.model = genai.GenerativeModel(model_name)

    def retrieve_context(self, query, n_results=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        contexts = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context_text = "\n\n".join(contexts)

        sections = []
        pages = []
        for meta in metadatas:
            section = meta.get("section")
            page = meta.get("page")
            if section and section not in sections:
                sections.append(section)
            if page and page not in pages:
                pages.append(page)

        return {
            "context": context_text,
            "sections": sections,
            "pages": pages
        }

    def answer_question(self, query):
        context_info = self.retrieve_context(query)

        prompt = f"""
You are a helpful AI assistant created to answer history questions based on provided context.

CONTEXT:
{context_info['context']}

QUESTION:
{query}

INSTRUCTIONS:
1. Answer the question only based on the context provided.
2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."
3. Provide a concise but complete answer.
4. Don't mention the context in your answer.
5. Don't use phrases like "According to the context" or "Based on the provided information."

ANSWER:
"""

        response = self.model.generate_content(prompt)
        answer = response.text.strip()

        return {
            "answer": answer,
            "context": context_info["context"],
            "sections": context_info["sections"],
            "pages": context_info["pages"]
        }
