import pdfplumber
import re
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd
import json
import logging
from typing import List, Dict, Optional

# Download punkt tokenizer if not already done
nltk.download('punkt', quiet=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_chunks_with_metadata(
    pdf_path: str,
    chunk_size: int = 5,
    min_sentence_length: int = 30,
    section_patterns: Optional[List[str]] = None
) -> List[Dict]:
    """
    Extracts text chunks from a PDF, grouped by sentence and annotated with page and section metadata.

    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Number of sentences per chunk.
        min_sentence_length (int): Minimum sentence length to include.
        section_patterns (List[str], optional): Regex patterns to detect section headings.

    Returns:
        List[Dict]: List of chunk dicts with 'text', 'pages', and 'sections' keys.
    """
    if section_patterns is None:
        # More flexible section heading patterns
        section_patterns = [
            r"^(Chapter|Section|Part)?\s*\d+[\.:]?",  # e.g., Chapter 1, Section 2.1
            r"^(Chapter|Section|Part)?\s*[IVXLC]+\s*[\.:]?",  # Roman numerals
            r"^(Introduction|Conclusion|Abstract|Summary)$",  # Common section titles
            r"^[A-Z][A-Za-z\s]{1,50}$"  # Lines with capitalized words (possible headings)
        ]

    chunks = []
    current_section = "Unknown Section"
    current_chunk = []
    current_chunk_pages = set()
    current_chunk_sections = set()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Opened PDF: {pdf_path} with {len(pdf.pages)} pages")

            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    logger.warning(f"Page {page_num} has no extractable text")
                    continue

                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Detect section headings
                    for pattern in section_patterns:
                        if re.match(pattern, line, re.IGNORECASE):
                            current_section = line.strip()
                            logger.info(f"Detected section heading on page {page_num}: {current_section}")
                            break

                    sentences = sent_tokenize(line)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) < min_sentence_length:
                            continue

                        current_chunk.append(sentence)
                        current_chunk_pages.add(page_num)
                        current_chunk_sections.add(current_section)

                        if len(current_chunk) >= chunk_size:
                            chunks.append({
                                "text": " ".join(current_chunk),
                                "pages": sorted(current_chunk_pages),
                                "sections": sorted(current_chunk_sections)
                            })
                            current_chunk = []
                            current_chunk_pages = set()
                            current_chunk_sections = set()

            # Add any leftover sentences as a final chunk
            if current_chunk:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "pages": sorted(current_chunk_pages),
                    "sections": sorted(current_chunk_sections)
                })

    except Exception as e:
        logger.error(f"Error processing PDF '{pdf_path}': {e}")
        raise

    logger.info(f"Extracted {len(chunks)} chunks from PDF")
    return chunks


def clean_text(text: str) -> str:
    """
    Cleans text by removing repeated characters and extra whitespace.

    Args:
        text (str): Input text.

    Returns:
        str: Cleaned text.
    """
    # Remove repeated characters (e.g., "aaa" -> "a")
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def save_chunks_to_csv(chunks: List[Dict], csv_path: str) -> None:
    """
    Saves extracted chunks to a CSV file.

    Args:
        chunks (List[Dict]): List of chunk dicts.
        csv_path (str): Output CSV file path.
    """
    df = pd.DataFrame(chunks)
    df.to_csv(csv_path, index=False)
    logger.info(f"Chunks saved to CSV: {csv_path}")


def save_chunks_to_json(chunks: List[Dict], json_path: str) -> None:
    """
    Saves extracted chunks to a JSON file.

    Args:
        chunks (List[Dict]): List of chunk dicts.
        json_path (str): Output JSON file path.
    """
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)
    logger.info(f"Chunks saved to JSON: {json_path}")


if __name__ == "__main__":
    PDF_PATH = "data/textbook.pdf"  # Change to your PDF path
    CHUNK_SIZE = 4
    MIN_SENTENCE_LENGTH = 30
    CSV_PATH = "outputs/chunks.csv"
    JSON_PATH = "outputs/chunks.json"

    chunks = extract_chunks_with_metadata(
        pdf_path=PDF_PATH,
        chunk_size=CHUNK_SIZE,
        min_sentence_length=MIN_SENTENCE_LENGTH
    )

    # Clean chunk texts
    for chunk in chunks:
        chunk["text"] = clean_text(chunk["text"])

    save_chunks_to_csv(chunks, CSV_PATH)
    save_chunks_to_json(chunks, JSON_PATH)
