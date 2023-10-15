from fastapi import FastAPI
from typing import Dict

app = FastAPI()


@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "Hello, World!"}
