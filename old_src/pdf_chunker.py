import pdfplumber
import re
import nltk
from nltk.tokenize import sent_tokenize
import pandas as pd
import json

# Download punkt tokenizer if not already done
nltk.download('punkt', quiet=True)

def extract_chunks_with_metadata(pdf_path, chunk_size, min_sentence_length):
    """
    Extracts text chunkas from a PDF, grouped by sentence and annotated with page and section metadata.

    Parameters:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): Number of sentences per chunk.
        min_sentence_length (int): Minimum sentence length to include.

    Returns:
        List[dict]: List of chunk dicts with 'text', 'page', and 'section' keys.
    """
    chunks = []
    current_section = "Unknown Section"
    current_chunk = []
    current_chunk_pages = set()
    current_chunk_sections = set()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')
                for line in lines:
                    line = line.strip()

                    # Detect section headings (tweak regex as needed)
                    if re.match(r"^(Chapter|Section)?\s?\d+[\.:]?", line, re.IGNORECASE):
                        current_section = line.strip()

                    sentences = sent_tokenize(line)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) < min_sentence_length:
                            continue

                        current_chunk.append(sentence)
                        current_chunk_pages.add(page_num)
                        current_chunk_sections.add(current_section)

                        # When chunk size reached, save it
                        if len(current_chunk) >= chunk_size:
                            chunks.append({
                                "text": " ".join(current_chunk),
                                "pages": sorted(current_chunk_pages),
                                "sections": sorted(current_chunk_sections)
                            })
                            current_chunk = []
                            current_chunk_pages = set()
                            current_chunk_sections = set()
            # Catch leftover text after all pages processed
            if current_chunk:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "pages": sorted(current_chunk_pages),
                    "sections": sorted(current_chunk_sections)
                })

    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")

    return chunks

def clean_text(text):
    # Remove repeated characters like "MMMaaacccaaadddaaammm"
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    # Optional: Strip weird characters, double spaces, etc.
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def save_chunks_to_csv(chunks, csv_path):
    """
    Saves extracted chunks to a CSV file.

    Parameters:
        chunks (List[dict]): List of chunk dicts.
        csv_path (str): Output CSV file path.
    """
    df = pd.DataFrame(chunks)
    df.to_csv(csv_path, index=False)
    print(f"Chunks saved to CSV: {csv_path}")


def save_chunks_to_json(chunks, json_path):
    """
    Saves extracted chunks to a JSON file.

    Parameters:
        chunks (List[dict]): List of chunk dicts.
        json_path (str): Output JSON file path.
    """
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)
    print(f"Chunks saved to JSON: {json_path}")

if __name__ == "__main__":
    pdf_path = "../data/textbook.pdf"
    chunk_size = 5
    min_sentence_length = 30
    chunks = extract_chunks_with_metadata(pdf_path,chunk_size, min_sentence_length)
    for chunk in chunks:
        chunk["text"] = clean_text(chunk["text"])
    # print(chunks[:3])
    save_chunks_to_csv(chunks, "../data/chunks.csv")
    save_chunks_to_json(chunks, "../data/chunks.json")
