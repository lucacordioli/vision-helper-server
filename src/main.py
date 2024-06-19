import json
import os
import shutil
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form
from starlette.middleware.cors import CORSMiddleware

from src.utils.functions import get_info_from_id, get_id_from_text
from src.utils.knowledge import Knowledge

app = FastAPI()
knowledge = Knowledge()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/add-document")
async def add_document(doc_id: Annotated[str, Form()], file: UploadFile):
    destination_folder = "documents"
    import os
    os.makedirs(destination_folder, exist_ok=True)
    file_name = doc_id + ".pdf"

    file_path = os.path.join(destination_folder, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    knowledge.add_pdf(file_path, doc_id)

    return {"message": f"File '{file.filename}' salvato con successo come '{file_name}'"}


@app.get("/get-all-documents")
async def get_all_documents():
    return knowledge.get_all_documents()


@app.delete("/delete-document")
async def delete_document(doc_id: str):
    knowledge.delete_item(doc_id)

    destination_folder = "documents"
    file_path = os.path.join(destination_folder, doc_id + ".pdf")
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": f"Document with ID '{doc_id}' deleted successfully"}


@app.get("/info-from-id")
async def info_from_id(obj_id: int):
    with open('/Users/lucacordioli/Documents/Lavori/polimi/TESI/visionHelperSrv/data/data.json', 'r') as file:
        data = json.load(file)
        res = get_info_from_id(obj_id, data)
        return res


@app.get("/id-from-text")
async def id_from_text(text: str):
    with open('/Users/lucacordioli/Documents/Lavori/polimi/TESI/visionHelperSrv/data/data.json', 'r') as file:
        data = json.load(file)
        res = get_id_from_text(text, data)
        return res
