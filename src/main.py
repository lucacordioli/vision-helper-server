from fastapi import FastAPI, Request

from src.utils.llm import LLM

llm = LLM()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World, I am Vision Helper Server"}


@app.post("/answer")
async def answer(request: Request):
    body = await request.json()
    input_topic = body.get("question")
    try:
        res = llm.get_answer(input_topic)
        return {"answer": res}
    except Exception as e:
        return {"error": str(e)}
