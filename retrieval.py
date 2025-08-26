import io
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from config import embeddings
from utils import chunk_text

# Đường dẫn PDF cố định (có thể chuyển sang .env / tham số)
PDF_PATH = r"C:\Users\ta an\Desktop\AI_engineer_learning\RAG Advanced\Bài tập cấu trúc How much, how many.pdf"

vectordb = Chroma(embedding_function=embeddings)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

def read_pdf_bytes_from_path(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def extract_pdf_text(pdf_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

def ingest_fixed_pdf() -> None:
    docs: List[Document] = []
    try:
        b = read_pdf_bytes_from_path(PDF_PATH)
        text = extract_pdf_text(b)
        for i, ch in enumerate(chunk_text(text)):
            docs.append(Document(
                page_content=ch,
                metadata={"source": PDF_PATH, "kind": "pdf_path", "chunk": i}
            ))
        if docs:
            vectordb.add_documents(docs)
            print(f"✅ Đã nạp PDF: {PDF_PATH}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc PDF {PDF_PATH}: {e}")
