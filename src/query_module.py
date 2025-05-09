import chromadb
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse

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
        
        # Add user agent for responsible scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # URL cache to avoid repeated scraping of the same URLs
        self.url_content_cache = {}

    def retrieve_context(self, query, n_results=10):
        """Retrieve relevant context from the ChromaDB collection"""
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
            page = meta.get("page_number")  # Fixed: changed from "page" to "page_number"
            if section and section not in sections:
                sections.append(section)
            if page and page not in pages:
                pages.append(page)

        return {
            "context": context_text,
            "sections": sections,
            "pages": pages
        }
    
    def extract_urls_from_text(self, text):
        """Extract URLs from text using regex"""
        url_pattern = re.compile(r'https?://[^\s\"\'\)\>]+')
        urls = url_pattern.findall(text)
        # Clean URLs (remove trailing punctuation that might be included in the regex match)
        cleaned_urls = []
        for url in urls:
            if url.endswith(('.', ',', ')', ']', ';', ':', '"', "'")):
                url = url[:-1]
            cleaned_urls.append(url)
        return cleaned_urls
        
    def get_wikipedia_info(self, url, query):
        """Specialized extraction for Wikipedia articles"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the article title
            title = soup.find('h1', {'id': 'firstHeading'}).text if soup.find('h1', {'id': 'firstHeading'}) else "Unknown Title"
            
            # Find the infobox (right sidebar with key facts)
            infobox = soup.find('table', {'class': 'infobox'})
            infobox_data = ""
            
            if infobox:
                # Extract key-value pairs from infobox
                rows = infobox.find_all('tr')
                for row in rows:
                    header = row.find('th')
                    value = row.find('td')
                    if header and value:
                        header_text = header.get_text(strip=True)
                        value_text = value.get_text(strip=True)
                        infobox_data += f"{header_text}: {value_text}\n"
            
            # Find main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            
            # Extract first few paragraphs (usually biographical info)
            paragraphs = content_div.find_all('p', recursive=False)[:5] if content_div else []
            intro_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
            
            # For biographical articles, specifically look for birth information
            birth_info = ""
            
            # Look for date of birth in the first few paragraphs
            birth_date_pattern = r'born (\w+ \d+,? \d{4})'
            birth_matches = re.search(birth_date_pattern, intro_text)
            if birth_matches:
                birth_info += f"Birth date: {birth_matches.group(1)}\n"
                
            # Look for specific sections that might contain biographical info
            if 'birth' in query.lower() or 'born' in query.lower():
                for heading in soup.find_all(['h2', 'h3']):
                    heading_text = heading.get_text().lower()
                    if 'early' in heading_text or 'life' in heading_text or 'birth' in heading_text or 'personal' in heading_text:
                        section = []
                        for sibling in heading.find_next_siblings():
                            if sibling.name and sibling.name.startswith('h'):
                                break
                            if sibling.name == 'p':
                                section.append(sibling.get_text(strip=True))
                        
                        section_text = "\n".join(section)
                        if section_text:
                            birth_info += f"From '{heading.get_text(strip=True)}' section:\n{section_text[:500]}...\n\n"
                        
                        # Look for specific dates in this section
                        date_pattern = r'\b\d{1,2}\s+\w+\s+\d{4}\b|\b\w+\s+\d{1,2},?\s+\d{4}\b'
                        dates = re.findall(date_pattern, section_text)
                        if dates:
                            birth_info += f"Dates mentioned: {', '.join(dates)}\n"
            
            # Combine all extracted information
            wiki_content = f"WIKIPEDIA ARTICLE: {title}\n\n"
            
            if infobox_data:
                wiki_content += f"KEY FACTS:\n{infobox_data}\n\n"
                
            if birth_info:
                wiki_content += f"BIRTH INFORMATION:\n{birth_info}\n\n"
            
            wiki_content += f"INTRODUCTION:\n{intro_text[:1000]}...\n"
            
            return wiki_content
            
        except Exception as e:
            print(f"Error processing Wikipedia page {url}: {str(e)}")
            return f"Error accessing Wikipedia: {str(e)}"
    
    def scrape_web_content(self, url, query):
        """
        Scrape content from a single URL with enhanced extraction
        
        Args:
            url (str): URL to scrape
            query (str): The user's query to guide extraction
            
        Returns:
            str: Extracted text content
        """
        # Check cache first
        cache_key = f"{url}_{query}"
        if cache_key in self.url_content_cache:
            return self.url_content_cache[cache_key]
            
        try:
            # Parse URL to determine appropriate handling
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Skip certain domains that might block scraping
            if any(blocked in domain for blocked in ['instagram.com', 'facebook.com']):
                return f"Content from {url} unavailable (social media content)"
            
            # Special handling for Wikipedia
            if 'wikipedia.org' in domain:
                content = self.get_wikipedia_info(url, query)
                self.url_content_cache[cache_key] = content
                return content
                
            # Default handling for other sites
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove non-content elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
                
            # Try to find main content
            main_content = None
            for selector in ['article', 'main', '.main-content', '#content', '.content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            # If main content found, use it; otherwise use the whole body
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
                
            # Clean up text
            clean_text = re.sub(r'\s+', ' ', text).strip()
            
            # Look for specific information based on query
            query_terms = query.lower().split()
            
            # For birthday/birth date queries
            if any(term in query.lower() for term in ['birth', 'born', 'birthday']):
                # Look for dates in the text
                date_pattern = r'\b\d{1,2}\s+\w+\s+\d{4}\b|\b\w+\s+\d{1,2},?\s+\d{4}\b'
                dates = re.findall(date_pattern, clean_text)
                if dates:
                    clean_text = f"Dates found in the text: {', '.join(dates[:5])}\n\n" + clean_text
            
            # Truncate to reasonable size
            content = f"Source: {url}\n{clean_text[:3000]}... (content truncated)\n"
                
            # Cache the result
            self.url_content_cache[cache_key] = content
            return content
            
        except Exception as e:
            error_message = f"Error scraping {url}: {str(e)}"
            print(error_message)
            return error_message
    
    def find_relevant_urls(self, query):
        """Extract URLs from the prompt template and find the most relevant ones"""
        # The hardcoded URL list from the prompt
        prompt_template = """
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
"""
        
        all_urls = self.extract_urls_from_text(prompt_template)
        
        # Extract key terms from the query
        query_terms = query.lower().split()
        
        # Define categories for historical figures/topics
        topics = {
            'wright': ['wright', 'flight', 'airplane', 'flyer'],
            'hitler': ['hitler', 'nazi', 'germany', 'world war', 'ww2'],
            'marie antoinette': ['marie', 'antoinette', 'france', 'revolution', 'cake'],
            'sri lanka': ['sri', 'lanka', 'ceylon', 'education'],
            'mahaweli': ['mahaweli', 'irrigation', 'development']
        }
        
        # Identify which topic the query is about
        relevant_topic = None
        for topic, keywords in topics.items():
            if any(term in query.lower() for term in keywords):
                relevant_topic = topic
                break
        
        relevant_urls = []
        
        # If topic identified, get topic-specific URLs
        if relevant_topic:
            for url in all_urls:
                # For the specific topic, prioritize Wikipedia and authoritative sources
                if relevant_topic.lower() in url.lower():
                    relevant_urls.append(url)
                # Add general Wikipedia articles that likely contain biographical info
                elif 'wikipedia.org' in url and any(keyword in url.lower() for keyword in topics.get(relevant_topic, [])):
                    relevant_urls.append(url)
        
        # If no topic-specific URLs found or no topic identified, use more general approach
        if not relevant_urls:
            # Extract entity names from query (simple approach)
            potential_entities = [term for term in query_terms if term[0].isupper() or len(term) > 5]
            
            for url in all_urls:
                # Check if URL contains any entity name
                if any(entity in url.lower() for entity in potential_entities):
                    relevant_urls.append(url)
                # Include Wikipedia articles as they usually have comprehensive info
                elif 'wikipedia.org' in url and any(term in url.lower() for term in query_terms):
                    relevant_urls.append(url)
        
        # Always include Wikipedia as a backup for biographical/historical info
        wiki_urls = [url for url in all_urls if 'wikipedia.org' in url]
        for wiki_url in wiki_urls:
            if wiki_url not in relevant_urls:
                relevant_urls.append(wiki_url)
        
        # Limit number of URLs to process
        return relevant_urls[:5]

    def answer_question(self, query):
        """
        Answer a history question using both database context and web content
        
        Args:
            query (str): User's history question
            
        Returns:
            dict: Answer and metadata
        """
        # Get context from database
        context_info = self.retrieve_context(query)
        
        # Find relevant URLs for the query
        relevant_urls = self.find_relevant_urls(query)
        
        # Scrape content from each URL
        web_contents = []
        for url in relevant_urls:
            content = self.scrape_web_content(url, query)
            if content and not content.startswith("Error"):
                web_contents.append(content)
            # Be a good citizen
            time.sleep(1)
        
        # Combine all web content
        combined_web_content = "\n\n".join(web_contents)
        
        # Build the prompt
        prompt = f"""
You are Ravi's RAG Agent, an expert educational assistant specialized in history.

Your primary task is to answer student questions based ONLY on the provided web content and database context. Do NOT add any information that is not supported by these sources.

IMPORTANT:  
- If asked about dates, facts, or specific information clearly present in the web content, include those exact details in your answer.  
- If the context is incomplete or does not contain enough information to answer fully, politely state that the information is insufficient.

HOWEVER, if the question explicitly requests:  
- An answer based on general knowledge beyond the given context, or  
- A creative or opinion-based response (such as a sarcastic remark),  

then:  
- You may use your general knowledge or creative skills to answer the question.  
- Clearly indicate that this answer is based on general knowledge or is a creative response, not derived from the provided context.

Please follow these instructions carefully:  
1. Provide a clear, accurate, and concise answer in 5 to 20 sentences.  
2. Include key facts such as important dates, names, inventions, and their impacts where relevant.  
3. Use simple and clear language suitable for high school students.  
4. Organize your answer logically, and use bullet points if multiple items need listing.  
5. Avoid speculation or unrelated information unless the question explicitly allows general knowledge or creativity.  

---
WEB CONTENT:  
{combined_web_content}

DATABASE CONTEXT:  
{context_info['context']}

---

Example 1 (Context-based question):  
Question: What were the major inventions that helped improve transportation during the Industrial Revolution?  
Answer:  
Major inventions that improved transportation during the Industrial Revolution included the steam locomotive, which allowed faster movement of goods and people by rail, and the steamship, which improved sea travel. These inventions helped expand trade and communication, contributing to economic growth and the spread of ideas.

---

Example 2 (General knowledge question):  
Question: Who led the Allied forces during the D-Day invasion in World War II?  
Answer:  
This answer is based on general knowledge beyond the provided context. The Allied forces during the D-Day invasion in World War II were led by General Dwight D. Eisenhower.

---

Example 3 (Creative/sarcastic response):  
Question: I think the French colonialists were incredibly efficient, unlike the Spanish! Write a sarcastic remark about the Spanish colonialists.  
Answer:  
Based on creative input, a sarcastic remark could be: "Oh sure, the Spanish colonialists were so efficient—they really mastered the art of turning gold into endless paperwork and delays!"

---


Question: {query}
"""

        try:
            # Generate answer with context and web content
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            # If prompt is too long, create a shortened version
            shortened_prompt = self._create_shortened_prompt(query, context_info["context"], combined_web_content)
            response = self.model.generate_content(shortened_prompt)
            answer = response.text.strip()

        return {
            "answer": answer,
            "context": context_info["context"],
            "sections": context_info["sections"],
            "pages": context_info["pages"],
            "web_sources": relevant_urls
        }
    
    def _create_shortened_prompt(self, query, context, web_content):
        """Create a shortened prompt to handle token limit issues"""
        # Determine what to prioritize based on the query
        query_lower = query.lower()
        
        # For biographical questions, prioritize web content as it's likely more factual
        if any(term in query_lower for term in ['birth', 'born', 'birthday', 'date', 'when']):
            # Keep more web content than context
            if len(web_content) > 6000:
                web_shortened = web_content[:6000] + "... [content truncated]"
            else:
                web_shortened = web_content
                
            if len(context) > 2000:
                context_shortened = context[:2000] + "... [context truncated]"
            else:
                context_shortened = context
        else:
            # Balance between web and context
            total_chars = len(web_content) + len(context)
            if total_chars > 8000:
                # Proportional reduction
                web_ratio = len(web_content) / total_chars
                context_ratio = len(context) / total_chars
                
                web_shortened = web_content[:int(6000 * web_ratio)] + "... [content truncated]"
                context_shortened = context[:int(2000 * context_ratio)] + "... [context truncated]"
            else:
                web_shortened = web_content
                context_shortened = context
        
        return f"""
You are Ravi's RAG Agent, an expert educational assistant specialized in history.

Answer the following question based on the provided information.
Use simple language suitable for high school students, be accurate and concise (5-8 sentences).

IMPORTANT: For questions about dates, facts, or specific details, make sure to include that information explicitly in your answer.

WEB CONTENT:
{web_shortened}

DATABASE CONTEXT:
{context_shortened}

Question: {query}

Remember to answer only based on the information provided.
"""