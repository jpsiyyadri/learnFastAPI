import asyncio
import os

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               StreamingResponse)
from half_json.core import JSONFixer

app = FastAPI()
json_fixer = JSONFixer()

openai_api_key = "<token>"
model = "gpt-4o-mini"
url = "https://api.openai.com/v1/chat/completions"

schema = {
    "type": "object",
    "properties": {
        "prime_numbers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "integer"
                    }
                },
                "required": ["number"]
            }
        }
    },
}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/html", response_class=HTMLResponse)
def send_html_resp():
    return "<h1>Hello World</h1>"


@app.get("/json", response_class=JSONResponse)
def send_json_resp():
    return {"Hello": "World"}


@app.get("/stream-numbers-10")
def test_stream():
    async def generate():
        for i in range(10):
            yield f"data: number is {i}\n\n"
            await asyncio.sleep(1)
        yield "[DONE]"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/stream-openai-response", response_class=StreamingResponse)
async def stream_response() -> str:
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
    }

    async def generate():
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant.\
                                    You are here to help the user with their queries.\
                                    Always generate JSON output.\
                                    Don't add any extra information in the output.",
                            },
                            {
                                "role": "user",
                                "content": "Give the list of prime numbers below 100.\
                            The out put format should be a list of dictionaries like below.\
                            output:\
                            [{'number': 2},{'number': 3}, {'number': 5},...]\
                            ",
                            },
                        ],
                        "max_tokens": 1000,
                        "stream": True,
                        "response_format": {"type": "json_object"},
                        # "strict": True,
                    },
                ) as response:
                    async for chunk in response.aiter_text():
                        yield chunk
        except Exception as e:
            yield str(e)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/{filename}.html", response_class=FileResponse)
def send_file(filename: str):
    if os.path.exists(f"{filename}.html"):
        return f"{filename}.html"
    return {"error": "file not found"}, 404


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
