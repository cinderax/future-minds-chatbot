# pdf_processing.py
# Step 1 & 2: PDF Text Extraction and Chunking

import os
import re
import json
from typing import List, Dict, Tuple, Any, Optional
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
        
        # Keep track of current chapter/section across pages
        self.current_chapter = ""
        self.current_section = ""
        self.current_subsection = ""

    def extract_text_from_pdf(self) -> None:
        """Extract text and metadata from each page of the PDF."""
        print(f"\nExtracting text from {self.pdf_path}...")

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                print(f"Processing page {i+1}/{total_pages}", end="\r")
                
                # Extract text from page
                text = page.extract_text()
                if text:
                    # Clean text (remove excess whitespace, etc.)
                    text = self._clean_text(text)

                    # Extract section information using regex patterns
                    section_info = self._extract_section_info(text, i + 1)
                    
                    # Update current chapter/section if found
                    if section_info.get("chapter"):
                        self.current_chapter = section_info["chapter"]
                    if section_info.get("section"):
                        self.current_section = section_info["section"]
                    if section_info.get("subsection"):
                        self.current_subsection = section_info["subsection"]
                    
                    # Use the latest chapter/section info
                    metadata = {
                        "page_number": i + 1,
                        "section": self.current_section,
                        "subsection": self.current_subsection,
                        "chapter": self.current_chapter
                    }

                    # Store text and metadata
                    self.pages_text.append(text)
                    self.pages_metadata.append(metadata)

        print(f"\nExtracted {len(self.pages_text)} pages of text.")

        # Save raw extracted text for reference
        with open(os.path.join(self.output_dir, self.raw_pages_file_name), "w", encoding="utf-8") as f:
            json.dump({
                "pages_text": self.pages_text,
                "pages_metadata": self.pages_metadata
            }, f, indent=2)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing headers, footers, and excess whitespace."""
        # Remove common header/footer patterns
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)
        
        # Remove page numbers that appear alone on a line
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common footer text patterns
        text = re.sub(r'Copyright © \d{4}.*', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace while preserving paragraph breaks
        text = re.sub(r'\n{3,}', '\n\n', text)  # Replace excessive newlines
        text = re.sub(r' {2,}', ' ', text)  # Replace multiple spaces
        
        return text.strip()

    def _extract_section_info(self, text: str, page_number: int) -> Dict[str, str]:
        """
        Extract section, subsection, and chapter information from text.
        Uses multiple regex patterns to identify different textbook formatting styles.
        """
        section_info = {}
        
        # Multiple chapter patterns to handle different formats
        chapter_patterns = [
            r'(?:^|\n)(?:Chapter|CHAPTER)\s+(\d+)[:\.\s]+(.+?)(?=\n|$)',  # Standard "Chapter X: Title"
            r'(?:^|\n)(\d+)\.\s+(.+?)(?=\n\d+\.\d+|\n|$)',  # Format like "1. Chapter Title"
        ]
        
        # Multiple section patterns
        section_patterns = [
            r'(?:^|\n)(\d+\.\d+)\s+(.+?)(?=\n|$)',  # Standard decimal "1.1 Section Title"
            r'(?:^|\n)(\d+\.\d+\.\d+)\s+(.+?)(?=\n|$)',  # Deep section like "1.1.2 Subsection"
            r'(?:^|\n)(?:Section|SECTION)\s+(\d+\.\d+)[:\.\s]+(.+?)(?=\n|$)',  # Explicit "Section 1.1: Title"
        ]
        
        # Try all chapter patterns
        for pattern in chapter_patterns:
            chapter_match = re.search(pattern, text)
            if chapter_match:
                section_info["chapter"] = f"Chapter {chapter_match.group(1)}: {chapter_match.group(2).strip()}"
                break
        
        # Try all section patterns for main sections
        for pattern in section_patterns:
            section_matches = re.finditer(pattern, text)
            for match in section_matches:
                section_num = match.group(1)
                # Check if it's a subsection (has two decimal points)
                if section_num.count('.') > 1:
                    section_info["subsection"] = f"{section_num} {match.group(2).strip()}"
                else:
                    section_info["section"] = f"{section_num} {match.group(2).strip()}"
        
        # If we still don't have sections, try more generic headings (all caps, etc.)
        if not section_info.get("section") and not section_info.get("chapter"):
            heading_pattern = r'(?:^|\n)([A-Z][A-Z\s]+[A-Z])(?:\n|$)'
            heading_match = re.search(heading_pattern, text)
            if heading_match:
                heading = heading_match.group(1).strip()
                # Determine if it's likely a chapter or section based on length and content
                if len(heading) < 30 and any(word in heading for word in ["CHAPTER", "INTRODUCTION", "APPENDIX"]):
                    section_info["chapter"] = heading
                else:
                    section_info["section"] = heading

        return section_info

    def chunk_text(self,
                   chunk_size: int,
                   chunk_overlap: int,
                   file_name: str) -> None:
        """
        Split extracted text into overlapping chunks with headings and page numbers included.

        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            file_name: Base filename for saving output
        """
        print(f"Chunking text with size={chunk_size}, overlap={chunk_overlap}...")

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        for i, (text, metadata) in enumerate(zip(self.pages_text, self.pages_metadata)):
            # Compose heading prefix string
            heading_parts = []
            if metadata.get("chapter"):
                heading_parts.append(metadata["chapter"])
            if metadata.get("section"):
                heading_parts.append(metadata["section"])
            if metadata.get("subsection"):
                heading_parts.append(metadata["subsection"])
            heading_prefix = " | ".join(filter(None, heading_parts))  # Filter out empty strings
            if heading_prefix:
                heading_prefix = f"[{heading_prefix}]"

            # Prepend heading and page number to page text for context
            page_text_with_heading = f"{heading_prefix} (Page {metadata['page_number']})\n\n{text}"

            # Split page text into chunks
            page_chunks = text_splitter.create_documents([page_text_with_heading])

            for j, chunk in enumerate(page_chunks):
                chunk_text = chunk.page_content
                self.chunks.append(chunk_text)
                self.chunks_metadata.append({
                    "chunk_id": f"p{metadata['page_number']}_c{j}",
                    "page_number": metadata["page_number"],
                    "section": metadata.get("section", ""),
                    "subsection": metadata.get("subsection", ""),
                    "chapter": metadata.get("chapter", ""),
                    "chunk_index": j,
                })

        print(f"Created {len(self.chunks)} chunks from {len(self.pages_text)} pages.")

        # Combine chunk text and metadata into one dict per chunk
        combined_chunks = []
        for chunk_text, meta in zip(self.chunks, self.chunks_metadata):
            combined = {
                "text": chunk_text,
                "page_number": meta.get("page_number"),
                "section": meta.get("section", ""),
                "subsection": meta.get("subsection", ""),
                "chapter": meta.get("chapter", ""),
                "chunk_id": meta.get("chunk_id"),
                "chunk_index": meta.get("chunk_index")
            }
            combined_chunks.append(combined)

        # Save combined chunks to JSON
        with open(os.path.join(self.output_dir, f"{file_name}.json"), "w", encoding="utf-8") as f:
            json.dump({"chunks": combined_chunks}, f, indent=2)

        # Save metadata and chunk text separately as CSV
        with open(os.path.join(self.output_dir, f"{file_name}.csv"), mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["chunk_id", "page_number", "section", "subsection", "chapter", "chunk_index", "chunk_content"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for chunk, meta in zip(self.chunks, self.chunks_metadata):
                writer.writerow({
                    "chunk_id": meta["chunk_id"],
                    "page_number": meta["page_number"],
                    "section": meta["section"],
                    "subsection": meta["subsection"],
                    "chapter": meta["chapter"],
                    "chunk_index": meta["chunk_index"],
                    "chunk_content": chunk
                })

        print(f"Chunks and metadata saved to {self.output_dir} folder.")

    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the PDF to better understand its format."""
        chapter_count = 0
        section_count = 0
        subsection_count = 0
        
        # Count unique chapters and sections
        chapters = set()
        sections = set()
        subsections = set()
        
        for meta in self.pages_metadata:
            if meta.get("chapter"):
                chapters.add(meta["chapter"])
            if meta.get("section"):
                sections.add(meta["section"])
            if meta.get("subsection"):
                subsections.add(meta["subsection"])
        
        return {
            "total_pages": len(self.pages_text),
            "unique_chapters": len(chapters),
            "unique_sections": len(sections),
            "unique_subsections": len(subsections),
            "chapters": list(chapters)[:5],  # Show first 5 chapters as samples
            "sections": list(sections)[:5],  # Show first 5 sections as samples
        }

    def process(self, chunk_size: int, chunk_overlap: int, file_name: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process the PDF: extract text, clean it, and split into chunks.

        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            file_name: Base filename for saving output

        Returns:
            Tuple of (chunks, chunks_metadata)
        """
        self.extract_text_from_pdf()
        
        # Analyze and show structure information
        structure_info = self.analyze_structure()
        print("\nDocument Structure Analysis:")
        print(f"Total Pages: {structure_info['total_pages']}")
        print(f"Unique Chapters: {structure_info['unique_chapters']}")
        print(f"Unique Sections: {structure_info['unique_sections']}")
        print(f"Unique Subsections: {structure_info['unique_subsections']}")
        
        # If no chapters or sections were found, warn the user
        if structure_info['unique_chapters'] == 0 and structure_info['unique_sections'] == 0:
            print("\nWARNING: No chapters or sections were detected. The PDF might have a non-standard format.")
            print("You may need to customize the regex patterns in _extract_section_info() method.")
            
            # Ask if the user wants to continue
            response = input("\nContinue with chunking anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Processing canceled.")
                return self.chunks, self.chunks_metadata
        
        # Continue with chunking
        self.chunk_text(chunk_size, chunk_overlap, file_name)
        return self.chunks, self.chunks_metadata


def get_user_inputs() -> Tuple[str, int, int, str]:
    """
    Collect user inputs for PDF path, chunk size, chunk overlap, and file name.

    Returns:
        Tuple containing pdf_path, chunk_size, chunk_overlap, and file_name.
    """
    pdf_path = input("\nPath to pdf: ").strip()
    if not os.path.isfile(pdf_path):
        print("Error: The file does not exist. Please provide a valid file path.")
        exit(1)
    if not pdf_path.lower().endswith('.pdf'):
        print("Error: The file is not a valid PDF. Please provide a PDF file.")
        exit(1)

    chunk_size_input = input("\nChunk Size(Default-> 300-400): ").strip()
    chunk_size = int(chunk_size_input) if chunk_size_input else 300  # Default to 300 if no input

    chunk_overlap_input = input("\nChunk_overlap(Default-> 50-100): ").strip()
    chunk_overlap = int(chunk_overlap_input) if chunk_overlap_input else 75  # Default to 75 if no input

    file_name = input("\nIn which name we should save Chunks? ").strip()

    return pdf_path, chunk_size, chunk_overlap, file_name


def main():
    pdf_path, chunk_size, chunk_overlap, file_name = get_user_inputs()

    processor = TextbookProcessor(pdf_path, file_name)
    chunks, metadata = processor.process(chunk_size, chunk_overlap, file_name)

    print(f"\nProcessing complete. Generated {len(chunks)} chunks.")


if __name__ == "__main__":
    main()