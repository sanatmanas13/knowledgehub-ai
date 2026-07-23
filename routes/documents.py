from fastapi import APIRouter, UploadFile, File
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile=File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path,"wb") as buffer:
        buffer.write(await file.read())

    return {
        "filename": file.filename,
        "saved_to": str(file_path)
    }