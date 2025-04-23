from transformers import pipeline, Pipeline
from typing import Optional, List

class SummarizerAgent:
    def __init__(self, model_name: str = "facebook/bart-large-cnn", device: Optional[int] = None):
        self.summarizer: Pipeline = pipeline(
            "summarization",
            model=model_name,
            device=device if device is not None else -1
        )

    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        chunk_size: int = 900
    ) -> str:
        if not text or len(text.strip()) < 40:
            return text.strip()
        
        input_length = len(text.split())
        
        # Dynamically adjust max_length to be shorter than input length
        if max_length is None or max_length > input_length:
            max_length = max(100, int(input_length * 0.7))
        
        if min_length is None or min_length > max_length:
            min_length = max(50, int(max_length * 0.5))
        
        # If text is short enough, summarize directly
        if len(text) < chunk_size:
            try:
                summary_list = self.summarizer(
                    text, max_length=max_length, min_length=min_length, do_sample=False
                )
                return summary_list[0]['summary_text'].strip()
            except Exception as e:
                print(f"Summarization error: {e}")
                return text.strip()

        # For longer texts: chunk, summarize each, then summarize the summaries
        chunks = self._split_text(text, chunk_size)
        partial_summaries = []
        for chunk in chunks:
            try:
                chunk_input_length = len(chunk.split())
                chunk_max_length = max(100, int(chunk_input_length * 0.7))
                chunk_min_length = max(50, int(chunk_max_length * 0.5))
                summary = self.summarizer(
                    chunk, max_length=chunk_max_length, min_length=chunk_min_length, do_sample=False
                )[0]['summary_text'].strip()
                partial_summaries.append(summary)
            except Exception as e:
                print(f"Chunk summarization error: {e}")
                partial_summaries.append(chunk.strip())
        combined_summary = " ".join(partial_summaries)
        # Final summary for all combined
        try:
            combined_input_length = len(combined_summary.split())
            final_max_length = max(100, int(combined_input_length * 0.7))
            final_min_length = max(50, int(final_max_length * 0.5))
            final_summary = self.summarizer(
                combined_summary, max_length=final_max_length, min_length=final_min_length, do_sample=False
            )[0]['summary_text'].strip()
            return final_summary
        except Exception as e:
            print(f"Final summarization error: {e}")
            return combined_summary

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        import re
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
