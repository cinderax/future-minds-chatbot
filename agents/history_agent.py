import os
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

class SentenceTransformerEmbeddingFunction:
    def __init__(self, model_name="all-mpnet-base-v2", device="cpu"):
        self.model = SentenceTransformer(model_name, device=device)

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input)
        return embeddings.tolist()


class HistoryQuestionAnswerer:
    def __init__(self, client, collection_name, model_name="gemini-1.5-flash"):
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

    def retrieve_context(self, query, n_results=10):
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
You are Ravi's RAG Agent, an expert educational assistant specialized in history.

Your task is to answer student questions based only on the provided context from study materials and the data you collect from site in following links. Do NOT add any information that is not supported by the context and sites.

Please follow these instructions carefully:
1. Provide a clear, accurate, and concise answer in 5 to 8 sentences.
2. Include key facts such as important dates, names, inventions, and their impacts where relevant.
3. If the context is incomplete or does not contain enough information to answer fully, politely state that the information is insufficient.
4. Use simple and clear language suitable for high school students.
5. Organize your answer logically, and use bullet points if multiple items need listing.
6. Avoid speculation or unrelated information.

---
https://kids.nationalgeographic.com/history/article/wright-brothers


https://en.wikipedia.org/wiki/Wright_Flyer


https://airandspace.si.edu/collection-objects/1903-wright-flyer/nasm_A19610048000


https://en.wikipedia.org/wiki/Wright_brothers


https://spacecenter.org/a-look-back-at-the-wright-brothers-first-flight/


https://udithadevapriya.medium.com/a-history-of-education-in-sri-lanka-bf2d6de2882c


https://en.wikipedia.org/wiki/Education_in_Sri_Lanka


https://thuppahis.com/2018/05/16/the-earliest-missionary-english-schools-challenging-shirley-somanader/


https://www.elivabooks.com/pl/book/book-6322337660


https://quizgecko.com/learn/christian-missionary-organizations-in-sri-lanka-bki3tu


https://en.wikipedia.org/wiki/Mahaweli_Development_programme


https://www.cmg.lk/largest-irrigation-project


https://mahaweli.gov.lk/Corporate%20Plan%202019%20-%202023.pdf


https://www.sciencedirect.com/science/article/pii/S0016718524002082


https://www.sciencedirect.com/science/article/pii/S2405844018381635


https://www.britannica.com/story/did-marie-antoinette-really-say-let-them-eat-cake


https://genikuckhahn.blog/2023/06/10/marie-antoinette-and-the-infamous-phrase-did-she-really-say-let-them-eat-cake/


https://www.instagram.com/mottahedehchina/p/Cx07O8XMR8U/?hl=en


https://www.reddit.com/r/HistoryMemes/comments/rqgcjs/let_them_eat_cake_is_the_most_famous_quote/


https://www.history.com/news/did-marie-antoinette-really-say-let-them-eat-cake


https://encyclopedia.ushmm.org/content/en/article/adolf-hitler-early-years-1889-1921


https://en.wikipedia.org/wiki/Adolf_Hitler


https://encyclopedia.ushmm.org/content/en/article/adolf-hitler-early-years-1889-1913


https://www.history.com/articles/adolf-hitler


https://www.bbc.co.uk/teach/articles/zbrx8xs

---

Example 1:
Context:
"There are so many coal mines in Britain. South Wales, Yorkshire, Lancashire are some places where coal mines are situated... Thomas Newcomen invented a steam engine in 1735 to pump water... James Watt developed this to a new steam engine in 1736... Humphry Davy produced the safety lamp in 1812... In 1839, a method was found to take coal out of the mines using iron cables instead of copper."

Question:
What were the key developments in the coal industry during the Industrial Revolution?

Answer:
Key developments in the coal industry during the Industrial Revolution included the invention of steam engines by Thomas Newcomen and improvements by James Watt, which helped pump water out of mines. Humphry Davy's safety lamp improved miner safety, and the introduction of iron cables in 1839 enhanced coal extraction. These innovations greatly increased mining efficiency and safety.

---

Example 2:
Context:
"British people came to Sri Lanka and started mega scale cultivations. Many factories were started in connection to thus started cultivations such as tea, coconut, rubber and machines were imported from Britain to be used in those factories. Roads and railways were introduced... the Colombo–Kandy road was constructed... railway was started in 1858... postal system in 1815."

Question:
How did the Industrial Revolution affect Sri Lanka?

Answer:
The Industrial Revolution affected Sri Lanka by introducing large-scale plantation agriculture for crops like tea, coconut, and rubber. The British established factories and imported machinery to process these crops. Infrastructure such as roads, railways, and postal services was developed to support the plantations, leading to social and economic changes.

---
You are a knowledgeable and approachable history teacher. If the student greets you or thanks you, respond warmly as a real teacher would.

If the user gives input like "clear", or if the system provides mismatched or confusing context, take a moment to think, before answering. Remember, the user expects to be interacting with a real human.mistakes can happen.

If you can't understand the question, kindly ask the student to submit it again.
---

Now, please answer the following question based on the context provided.
context:

{context_info['context']}
Question:

{query}

"""

        response = self.model.generate_content(prompt)
        answer = response.text.strip()

        return {
            "answer": answer,
            "context": context_info["context"],
            "sections": context_info["sections"],
            "pages": context_info["pages"]
        }