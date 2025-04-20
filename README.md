# future-minds-chatbot
Multi-agent RAG chatbot for the Future Minds competition

#about pdf_chunker.py

- before run pdf_chunker.py, you can add "nltk.download('punkt')" code but its make code inefficient. so run this in python shell before execute the code.
~~~
import nltk
nltk.download('punkt')
~~~

- add this code to end of the pdf_chunker.py to check if it is working correctly.
~~~ if __name__ == "__main__":
    chunks = extract_chunks_with_metadata(pdf_path, chunk_size, min_sentence_length)
    print(f"Extracted {len(chunks)} chunks.")
    print("Sample output:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"Page: {chunk['page']}")
        print(f"Section: {chunk['section']}")
        print(f"Text: {chunk['text']}\n")
if __name__ == "__main__":
    chunks = extract_chunks_with_metadata(pdf_path, chunk_size, min_sentence_length)
    print(f"Extracted {len(chunks)} chunks.")
    print("Sample output:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"Page: {chunk['page']}")
        print(f"Section: {chunk['section']}")
        print(f"Text: {chunk['text']}\n")
~~~
