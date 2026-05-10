from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "AI Content Agent Running"}

@app.post("/generate")
def generate(data: PromptRequest):
    return {
        "prompt": data.prompt,
        "content": f"Generated content for: {data.prompt}"
    }