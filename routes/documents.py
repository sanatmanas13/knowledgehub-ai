import logging

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

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class QuestionRequest(BaseModel):
    question: str

@router.post("/upload")
async def upload_document(file: UploadFile=File(...)):

    logger.info("Uploading document: %s", file.filename)

    file_path = UPLOAD_DIR / file.filename

    with open(file_path,"wb") as buffer:
        buffer.write(await file.read())

    text = extract_text_from_pdf(file_path)

    c_text = clean_text(text)

    chunks = chunk_text(c_text)
    logger.info("Generated %d chunks", len(chunks))

    embeddings = generate_embeddings(chunks)

    chunks_db = store_embeddings(chunks,embeddings,file.filename)

    logger.info("stored %d chunks for %s", chunks_db, file.filename)

    return {
        "success": True,
        "message": "Document uploaded successfully.",
        "filename": file.filename,
        "chunks_stored": chunks_db
    }

@router.post("/ask")
async def ask_question(request: QuestionRequest):

    logger.info("Question received: %s", request.question)

    results = retrieve_chunks(request.question)
    if not results["documents"] or not results["documents"][0]:

        logger.warning("No relevant chunks found.")

        return {
            "success": False,
            "question": request.question,
            "answer": "I couldn't find any relevant information in the uploaded documents."
        }
    retrieved_chunks = results["documents"][0]

    logger.info("Retrieved %d relevant chunks", len(retrieved_chunks))

    messages = build_messages(
        request.question,
        retrieved_chunks
    )
    
    answer = generate_answer(messages)

    logger.info("Answer generated successfully.")

    return {
        "success": True,
        "question": request.question,
        "answer": answer
    }