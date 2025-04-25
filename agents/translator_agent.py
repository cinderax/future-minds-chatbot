import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class TranslatorAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Initialize the TranslatorAgent.

        Args:
            model_name (str): Gemini model name.
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=google_api_key)

        self.model = genai.GenerativeModel(model_name)
        
        # Dictionary of supported languages
        self.languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian", 
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "hi": "Hindi",
            "bn": "Bengali",
            "si": "Sinhala",
            "ta": "Tamil"
        }

    def get_supported_languages(self):
        """
        Returns a dictionary of supported languages.
        """
        return self.languages

    def translate(self, text, target_language="en"):
        """
        Translates the given text to the target language.

        Args:
            text (str): The text to translate.
            target_language (str): The language code to translate to (default: "en").

        Returns:
            dict: Dictionary containing the translated text and metadata.
        """
        if not text:
            return {"error": "No text provided"}
            
        # Get the language name
        language_name = self.languages.get(target_language, "Unknown")
        if language_name == "Unknown":
            return {"error": f"Unsupported language code: {target_language}"}
            
        prompt = f"""
Translate the following text into {language_name}. Use only that language, except for proper nouns or names, which should remain in English. Preserve meaning, tone, and formatting. Adapt cultural references or idioms as needed.

Text:
{text}

Translation ({language_name}):
"""

        response = self.model.generate_content(prompt)
        translation = response.text.strip()
        
        return {
            "original": text,
            "translation": translation,
            "target_language": target_language,
            "target_language_name": language_name
        }