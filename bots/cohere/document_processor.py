import docx
import os
from typing import List

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def chunk_text(text: str, chunk_size: int = 256) -> List[str]:
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def process_documents(document_paths: List[str]) -> List[str]:
    all_chunks = []
    for path in document_paths:
        if path.endswith('.docx'):
            text = extract_text_from_docx(path)
        else:
            with open(path, 'r') as file:
                text = file.read()
        chunks = chunk_text(text)
        all_chunks.extend(chunks)
    return all_chunks
