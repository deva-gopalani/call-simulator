import httpx
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

async def perform_llm_request(user_query):
    try:
        url = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('HUGGING_FACE_LLM_KEY')}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "microsoft/Phi-3-mini-4k-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": f"For the below asked question generate a short answer \n {user_query}"
                }
            ],
            "max_tokens": 500,
            "stream": False
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Exception occurred in LLM request - {e}")


@app.websocket("/bot/{user_id}/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    try:
        await websocket.accept()
        print(f"Websocket connection received for user_id = {user_id} and session_id = {session_id}")
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            llm_response = await perform_llm_request(data["user_query"])
            data["sender"] = "server"
            data["llm_response"] = llm_response
            await websocket.send_json(data)
    except WebSocketDisconnect as wd:
        print(f"Websocket got disconnected - {wd}")
    except Exception as e:
        print(f"Exception occured in websocket connection accepting handler - {e}")