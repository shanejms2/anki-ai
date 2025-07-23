from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DummyModel(BaseModel):
    foo: str
    bar: int

@app.post("/test")
async def test(dummy: DummyModel):
    print("DUMMY ENDPOINT CALLED:", dummy)
    return dummy