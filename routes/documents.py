from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from utils.pdf_parser import extract_text_from_pdf
from utils.text_chunker import chunk_text
from utils.text_cleaner import clean_text

from utils.embedding import generate_embeddings
from utils.vector_store import store_embeddings, retrieve_chunks

from utils.message_builder import build_messages
from services.llm_service import generate_answer

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class QuestionRequest(BaseModel):
    question: str

@router.post("/upload")
async def upload_document(file: UploadFile=File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path,"wb") as buffer:
        buffer.write(await file.read())

    text = extract_text_from_pdf(file_path)

    c_text = clean_text(text)

    chunks = chunk_text(c_text)

    embeddings = generate_embeddings(chunks)

    chunks_db = store_embeddings(chunks,embeddings,file.filename)

    return {
        "message": "Document uploaded successfully.",
        "filename": file.filename,
        "saved_to": str(file_path),
        "chunks_stored": chunks_db
    }

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    results = retrieve_chunks(request.question)
    if not results["documents"] or not results["documents"][0]:
        return {
            "question": request.question,
            "answer": "I couldn't find any relevant information in the uploaded documents."
        }
    retrieved_chunks = results["documents"][0]

    if not retrieve_chunks:
        return{
            "questions": request.question,
            "answer": "I couldn't find any relevant information in the uploaded documents."
        }

    messages = build_messages(
        request.question,
        retrieved_chunks
    )
    
    answer = generate_answer(messages)

    return {
        "question": request.question,
        "answer": answer
    }