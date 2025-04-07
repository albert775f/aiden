from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS erlauben (für Zugriff vom Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"

@app.post("/chat")
async def chat(req: ChatRequest):
    response = openai.ChatCompletion.create(
        model=req.model,
        messages=[
            {"role": "system", "content": "Du bist Aiden, ein hilfsbereiter KI-Operator."},
            {"role": "user", "content": req.message}
        ]
    )
    reply = response.choices[0].message["content"]
    return { "reply": reply }

class FileRequest(BaseModel):
    filename: str
    content: str

@app.post("/create_file")
def create_file(req: FileRequest):
    file_path = WORKSPACE_DIR / req.filename
    file_path.write_text(req.content, encoding="utf-8")
    return { "status": "created", "path": str(file_path) }

@app.get("/list_files")
def list_files():
    return { "files": [f.name for f in WORKSPACE_DIR.iterdir() if f.is_file()] }

@app.get("/read_file")
def read_file(filename: str):
    file_path = WORKSPACE_DIR / filename
    if file_path.exists():
        return { "content": file_path.read_text(encoding="utf-8") }
    return { "error": "Datei nicht gefunden" }