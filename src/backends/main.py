import os
import signal
import sys
import asyncio
import threading
from typing import TypedDict
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from .inference import infer_text_api

PORT_API = 8008

server_instance = None  # Global reference to the Uvicorn server instance

app = FastAPI(
    title="API server",
    version="0.1.0",
)

# Configure CORS settings
origins = [
    "*",  # to whitelist any url, REMOVE THIS FOR PRODUCTION!!!
    # "http://localhost:3000", # for dev
    # "https://your-web-ui.com", # for prod
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tell client we are ready to accept requests.
# This is a mock func, modify to your needs.
@app.get("/v1/connect")
def connect_to_api_server():
    print("[server] Connecting to server...", flush=True)
    host = f"http://localhost:{PORT_API}"
    return {
        "message": f"Connected to api server on port {PORT_API}. Refer to '{host}/docs' for api docs.",
        "data": {
            "port": PORT_API,
            "pid": os.getpid(),
            "host": host,
        },
    }


class T_Query(TypedDict):
    prompt: str


# Mock text inference endpoint, here for inspiration.
@app.post("/v1/completions")
def llm_completion(payload: T_Query = Body(...)):
    return infer_text_api.completions(payload)


# Programmatically force shutdown this sidecar.
def kill_process():
    os.kill(os.getpid(), signal.SIGINT)  # This force closes this script.


# Programmatically startup the api server
def start_api_server(**kwargs):
    global server_instance
    port = kwargs.get("port", PORT_API)
    try:
        if server_instance is None:
            print("[sidecar] Starting API server...", flush=True)
            config = Config(app, host="0.0.0.0", port=port, log_level="info")
            server_instance = Server(config)
            # Start the ASGI server
            asyncio.run(server_instance.serve())
        else:
            print(
                "[sidecar] Failed to start new server. Server instance already running.",
                flush=True,
            )
    except Exception as e:
        print(f"[sidecar] Error, failed to start API server {e}", flush=True)


# Handle the stdin event loop. This can be used like a CLI.
def stdin_loop():
    print("[sidecar] Waiting for commands...", flush=True)
    while True:
        # Read input from stdin.
        user_input = sys.stdin.readline().strip()

        # Check if the input matches one of the available functions
        match user_input:
            case "sidecar shutdown":
                print("[sidecar] Received 'sidecar shutdown' command.", flush=True)
                kill_process()
            case _:
                print(
                    f"[sidecar] Invalid command [{user_input}]. Try again.", flush=True
                )


# Start the input loop in a separate thread
def start_input_thread():
    try:
        input_thread = threading.Thread(target=stdin_loop)
        input_thread.daemon = True  # so it exits when the main program exits
        input_thread.start()
    except:
        print("[sidecar] Failed to start input handler.", flush=True)


if __name__ == "__main__":
    # You can spawn sub-processes here before the main process.
    # new_command = ["python", "-m", "some_script", "--arg", "argValue"]
    # subprocess.Popen(new_command)

    # Listen for stdin from parent process
    start_input_thread()

    # Starts API server, blocks further code from execution.
    start_api_server()
