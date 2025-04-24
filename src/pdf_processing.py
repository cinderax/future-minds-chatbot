# pdf_processing.py
# Step 1 & 2: PDF Text Extraction and Chunking

import os
import re
import json
from typing import List, Dict, Tuple, Any
import pdfplumber
import csv
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextbookProcessor:
    def __init__(self, pdf_path: str, file_name: str, output_dir: str = "processed_data"):
        """
        Initialize the TextbookProcessor with paths to PDF, output directory, and file name.
        
        Args:
            pdf_path: Path to the PDF file
            file_name: Name to use for saving processed files
            output_dir: Directory to store processed chunks and metadata
        """
        self.file_name = file_name
        self.raw_pages_file_name = f"raw_pages({file_name}).json"
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize storage for extracted text and metadata
        self.pages_text = []
        self.pages_metadata = []
        self.chunks = []
        self.chunks_metadata = []

    def extract_text_from_pdf(self) -> None:
        """Extract text and metadata from each page of the PDF."""
        print(f"\nExtracting text from {self.pdf_path}...")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extract text from page
                text = page.extract_text()
                if text:
                    # Clean text (remove excess whitespace, etc.)
                    text = self._clean_text(text)
                    
                    # Extract section information using regex patterns
                    section_info = self._extract_section_info(text)
                    
                    # Store text and metadata
                    self.pages_text.append(text)
                    self.pages_metadata.append({
                        "page_number": i + 1,
                        "section": section_info.get("section", ""),
                        "subsection": section_info.get("subsection", ""),
                        "chapter": section_info.get("chapter", "")
                    })
                    
        print(f"Extracted {len(self.pages_text)} pages of text.")
        
        # Save raw extracted text for reference
        with open(os.path.join(self.output_dir, self.raw_pages_file_name), "w") as f:
            json.dump({
                "pages_text": self.pages_text,
                "pages_metadata": self.pages_metadata
            }, f, indent=2)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing headers, footers, and excess whitespace."""
        # Remove common header/footer patterns (customize based on your PDF)
        text = re.sub(r'Page \d+ of \d+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def _extract_section_info(self, text: str) -> Dict[str, str]:
        """
        Extract section, subsection, and chapter information from text.
        
        Note:
            The `chapter_pattern` and `section_pattern` regex patterns are examples and may not work for all textbook structures.
            Users should customize these patterns based on the specific format and structure of their PDF.
        """
        section_info = {}
        
        # Example patterns - customize based on your textbook's structure
        chapter_pattern = r'Chapter\s+(\d+)[:\s]+(.*?)(?=\n|$)'
        section_pattern = r'(\d+\.\d+)\s+(.*?)(?=\n|$)'
        
        # Extract chapter
        chapter_match = re.search(chapter_pattern, text)
        if chapter_match:
            section_info["chapter"] = f"{chapter_match.group(1)}: {chapter_match.group(2)}"
        
        # Extract section
        section_match = re.search(section_pattern, text)
        if section_match:
            section_info["section"] = f"{section_match.group(1)} {section_match.group(2)}"
        
        return section_info

    def chunk_text(self, 
                  chunk_size: int, 
                  chunk_overlap: int,
                  file_name: str) -> None:
        """
        Split extracted text into overlapping chunks.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        
        Notes:
            The `separators` parameter in `RecursiveCharacterTextSplitter` defines the order of delimiters 
            (e.g., paragraphs, sentences, spaces) to prioritize when splitting text. It ensures that chunks 
            are split at meaningful boundaries, improving readability and context retention.
        """
        print(f"Chunking text with size={chunk_size}, overlap={chunk_overlap}...")
        separators=["\n\n", "\n", ". ", " "]
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Process each page
        for i, (text, metadata) in enumerate(zip(self.pages_text, self.pages_metadata)):
            # Split text into chunks
            page_chunks = text_splitter.create_documents([text])
            
            # Create metadata for each chunk
            for j, chunk in enumerate(page_chunks):
                self.chunks.append(chunk.page_content)
                self.chunks_metadata.append({
                    "chunk_id": str(f"p{metadata['page_number']}_c{j}"),
                    "page_number": int(metadata["page_number"]),
                    "section": str(metadata["section"]),
                    "subsection": str(metadata["subsection"]),
                    "chapter": str(metadata["chapter"]),
                    "chunk_index": int(j),
                })
        
        print(f"Created {len(self.chunks)} chunks from {len(self.pages_text)} pages.")
        
        # Save chunks and metadata
        # Ensure all data is JSON-serializable
        serializable_chunks = self.chunks
        serializable_metadata = [
            metadata
            for metadata in self.chunks_metadata
        ]
        
        with open(os.path.join(self.output_dir, f"{file_name}.json"), "w") as f:
            json.dump({
                "chunks": serializable_chunks,
                "metadata": serializable_metadata
            }, f, indent=2)
               
        with open(os.path.join(self.output_dir, f"{file_name}.csv"), mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["chunk_id", "page_number", "section", "subsection", "chapter", "chunk_index", "chunk_content"])
            writer.writeheader()
            for chunk, metadata in zip(self.chunks, self.chunks_metadata):
                writer.writerow({
                    "chunk_id": metadata["chunk_id"],
                    "page_number": metadata["page_number"],
                    "section": metadata["section"],
                    "subsection": metadata["subsection"],
                    "chapter": metadata["chapter"],
                    "chunk_index": metadata["chunk_index"],
                    "chunk_content": chunk  # Ensure this matches the fieldname
                })

        print(f"Chunks and metadata saved to {self.output_dir} Folder.")

    def process(self, chunk_size: int, chunk_overlap: int, file_name:str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process the PDF: extract text, clean it, and split into chunks.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            Tuple of (chunks, chunks_metadata)
        """
        self.extract_text_from_pdf()
        self.chunk_text(chunk_size, chunk_overlap, file_name)
        return self.chunks, self.chunks_metadata


def get_user_inputs() -> Tuple[str, int, int, str]:
    """
    Collect user inputs for PDF path, chunk size, chunk overlap, and file name.
    
    Returns:
        Tuple containing pdf_path, chunk_size, chunk_overlap, and file_name.
    """
    pdf_path = input("\nPath to pdf: ")
    if not os.path.isfile(pdf_path):
        print("Error: The file does not exist. Please provide a valid file path.")
        exit(1)
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: The file is not a valid PDF. Please provide a PDF file.")
        exit(1)

    chunk_size_input = input("\nChunk Size(Default-> 300-400): ")
    chunk_size = int(chunk_size_input) if chunk_size_input.strip() else 300  # Default to 300 if no input

    chunk_overlap_input = input("\nChunk_overlap(Default-> 50-100): ")
    chunk_overlap = int(chunk_overlap_input) if chunk_overlap_input.strip() else 75  # Default to 75 if no input

    file_name = input("\nIn which name we should save Chunks? ")

    return pdf_path, chunk_size, chunk_overlap, file_name


def main():
    pdf_path, chunk_size, chunk_overlap, file_name = get_user_inputs()

    processor = TextbookProcessor(pdf_path, file_name)
    chunks, metadata = processor.process(chunk_size, chunk_overlap, file_name)

    print(f"\nProcessing complete. Generated {len(chunks)} chunks.")


if __name__ == "__main__":
    main()