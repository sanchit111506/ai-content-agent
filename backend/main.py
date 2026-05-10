from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator import generate_content

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "AI Content Agent Running"}

@app.post("/generate")
def generate(data: PromptRequest):

    result = generate_content(data.prompt)

    return {
        "status": "success",
        "prompt": data.prompt,
        "generated_content": str(result)
    }