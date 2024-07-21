import json
import os
import shutil
from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Form, Query, Body
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from src.utils import shared_data
from src.utils.functions import get_info_from_id, get_id_from_text
from src.utils.graph import WorkflowManager
from src.utils.knowledge import Knowledge
from src.utils.shared_data import initialize_data

global json_data

app = FastAPI()
knowledge = Knowledge()
shared_data.initialize_data('/Users/lucacordioli/Documents/Lavori/polimi/TESI/visionHelperSrv/data/data.json')
workflow_manager = WorkflowManager()

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


@app.get("/documents")
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
async def info_from_id(obj_id: str):
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


class ChatRequest(BaseModel):
    text: str
    deck: str


@app.post("/chat")
async def chat(request: ChatRequest = Body(...)):

    initialize_data(request.deck)
    res = workflow_manager.run(request.text)

    output = {"message": res["messages"][-1].content}
    if "item_id" in res:
        output["item"] = res["item_id"]
    if "pdf_name" in res:
        output["pdf_name"] = res["pdf_name"]
    if "page_n" in res:
        output["page_n"] = res["page_n"]
    return output
