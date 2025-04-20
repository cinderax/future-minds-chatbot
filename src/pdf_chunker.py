import pdfplumber
import re
import nltk
from nltk.tokenize import sent_tokenize

pdf_path = "../data/textbook.pdf"
chunk_size = 4
min_sentence_length = 30

def extract_chunks_with_metadata(pdf_path, chunk_size, min_sentence_length):

    """
    Extracts text chunks from a PDF, grouped by sentence and annotated with page and section metadata.
    
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

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')
            for line in lines:
                line = line.strip()

                # Detect section headings (tweak as needed for your PDF formatting)

                if re.match(r"^(Chapter|Section)?\s?\d+[\.:]?", line, re.IGNORECASE):
                    current_section = line

                sentences = sent_tokenize(line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) < min_sentence_length:
                        continue

                    current_chunk.append(sentence)

                    # When chunk size reached, save it
                    if len(current_chunk) >= chunk_size:
                        chunks.append({
                            "text": " ".join(current_chunk),
                            "page": page_num,
                            "section": current_section
                        })
                        current_chunk = []

    # Catch leftover text
    if current_chunk:
        chunks.append({
            "text": " ".join(current_chunk),
            "page": page_num,
            "section": current_section
        })

    return chunks

# Example usage:
# chunks = extract_chunks_with_metadata("path/to/your_textbook.pdf")
# print(chunks[:3])

