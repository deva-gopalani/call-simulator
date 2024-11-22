import uuid
import time
import json
import asyncio
from websockets import ConnectionClosedError, ConnectionClosedOK
from websockets.asyncio.client import connect
from utils import *


async def create_websocket_connect(uri, test_duration):
    stop_event = asyncio.Event()
    try:
        async with connect(uri=uri) as websocket:
            websocket_connection_time = time.time()
            async def receive_messages():
                try:
                    while not stop_event.is_set():
                        message = await websocket.recv()
                        print(f"Message recieved on websocket - {message}")
                except ConnectionClosedError as e:
                    print(f"Websocket closed with error - {e}")
                except ConnectionClosedOK as e:
                    print(f"Connection closed successfully")
                finally:
                    stop_event.set()

            async def send_messages():
                try:
                    while not stop_event.is_set():
                        if time.time() - websocket_connection_time < test_duration:
                            message = get_random_question()
                            await websocket.send(json.dumps({"sender": "client", "user_query": message}))
                            print(f"Message being sent to server - {message}")
                        else:
                            print("Closing websocket connection as test duration completed.")
                            await websocket.close()
                            stop_event.set()
                        await asyncio.sleep(10)
                except Exception as e:
                    print(f"Error in sending messages - {e}")

            await asyncio.gather(receive_messages(), send_messages())
    except Exception as e:
        print(f"Received error in create_websocket_connect - {e}")

async def main():
    tasks = []
    test_duration = 25 # in seconds
    number_of_users = 5
    for i in range(1, number_of_users + 1):
        tasks.append(create_websocket_connect(f"ws://localhost:8000/bot/user_{i}/{uuid.uuid4()}/ws", test_duration))
    await asyncio.gather(*tasks)

asyncio.run(main())
