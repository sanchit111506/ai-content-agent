from backend.chat import router as chat_router

from fastapi import FastAPI, UploadFile, File
import shutil
import os

from storage.ingest import ingest_pdf

app = FastAPI()

app.include_router(chat_router)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # Save uploaded PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Automatically ingest into RAG
    result = ingest_pdf(file_path)

    return {
        "message": "PDF uploaded and indexed successfully!",
        "filename": file.filename,
        "rag_result": result
    }