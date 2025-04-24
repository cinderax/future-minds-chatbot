import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class SummarizerAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Initialize the SummarizerAgent.

        Args:
            model_name (str): Gemini model name.
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=google_api_key)

        self.model = genai.GenerativeModel(model_name)
        
        # Summary length options
        self.length_options = {
            "brief": "1-2 sentences",
            "short": "1 paragraph (3-5 sentences)",
            "medium": "2-3 paragraphs",
            "detailed": "comprehensive summary with key points"
        }

    def get_length_options(self):
        """
        Returns a dictionary of available summary length options.
        """
        return self.length_options

    def summarize(self, text, length="medium"):
        """
        Summarizes the given text according to the specified length.

        Args:
            text (str): The text to summarize.
            length (str): The desired summary length (brief, short, medium, detailed).

        Returns:
            dict: Dictionary containing the summarized text and metadata.
        """
        if not text:
            return {"error": "No text provided"}
            
        # Get the length description
        length_desc = self.length_options.get(length, self.length_options["medium"])
            
        prompt = f"""
Summarize the following text in {length_desc}.
Focus on the main ideas, key points, and important details.
Maintain the factual accuracy and original meaning of the content.

Text to summarize:
{text}

Summary:
"""

        response = self.model.generate_content(prompt)
        summary = response.text.strip()
        
        return {
            "original": text,
            "summary": summary,
            "length": length,
            "length_description": length_desc
        }