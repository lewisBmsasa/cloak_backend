import subprocess
import os
import time
import logging
import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import ollama
import tempfile
import os
import time
from asyncio import run, ensure_future, gather
from pathlib import Path
from cloaking.presidio_requests import  anonymize_text_post,anonymize_pdf_results
from cloaking.presidio import anonymize_text, anonymize_pdf
from utils.requests.message_request import MessageRequest
from utils.constants.vars import system_prompts, base_options, UPLOAD_DIR

"""
SETUP
"""
global_base_model = "phi3"
parser = argparse.ArgumentParser(description="Local LLM Server")
parser.add_argument("--port", type=int, default=8000, help="Port for server")
parser.add_argument("--model", type=str, default=global_base_model, help="Model name to use")
args = parser.parse_args()
base_model = args.model
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
# Set the model directory
os.environ["OLLAMA_MODELS"] = os.path.abspath("./models")
# Path to log file
log_file_path = Path("logs.txt")

def start_ollama_server():
    global process
    try:
        process = subprocess.Popen(["./bin/ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Starting Ollama server...")
        print("Ollama server started in the background.")
        time.sleep(3)  # Give Ollama time to start
    except Exception as e:
        logging.error(f"Failed to start Ollama server: {e}")
        raise HTTPException(status_code=500, detail="Failed to start Ollama server")

def log_to_file(message: str):
    """Log messages to a file."""
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

async def async_chat_stream(model, messages, **kwargs):
   try:
        stream = ollama.chat(
            model=model, 
            messages=messages,
            **kwargs
        )
        for chunk in stream:
            yield chunk["message"]["content"]
   except Exception as e:
        logging.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail=f"Model streaming failed: {str(e)}")


async def split_into_chunks(input_text, chunk_size=100):
    """Split a string into chunks of a specific size."""
    words = input_text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

async def get_response_stream(model_name, system_prompt, user_message, chunking):
    """Stream results from the Ollama model asynchronously."""
    start_time = time.time()

    if chunking:
        prompt_chunks = await split_into_chunks(user_message)
    else:
        prompt_chunks = [user_message]
    results = []
    print("chuuuuunkkkks", prompt_chunks)
    
    for prompt_chunk in prompt_chunks:
        print("Processing chunk: ", prompt_chunk)
        logging.info(f"Processing chunk: {prompt_chunk}")
        buffer = ""
        last_parsed_content = ""
        
        async for chunk in async_chat_stream(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt_chunk}
            ],
            format="json",
            stream=True,
            options=base_options
        ):
            log_message = f"Result chunk: {chunk} (Time: {time.time() - start_time:.2f}s)"
            #print(log_message)
            logging.info(f"Result chunk: {chunk} (Time: {time.time() - start_time:.2f}s)")
            yield chunk
           
async def initialize_server(test_message: str):
    """Initialize the model on startup."""
    try:
        # Consume the async generator using async for
        async for _ in get_response_stream(base_model, system_prompts["detect"], test_message, True):
            pass  # You don't need to store the result, just need to consume it
        print("Server initialized successfully!")
    except Exception as e:
        print(f"Error initializing server: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("App is starting...")
    try:
        start_ollama_server()
        await initialize_server("Hi, welcome to Cloak!")
        yield
    finally:
        if process:
            process.terminate()
            logging.info("Ollama server terminated.")
        logging.info("App is shutting down...")

app = FastAPI()

# try:
#     nlp = spacy.load("en_core_web_sm")
#     print("spaCy model loaded successfully")
# except Exception as e:
#     print(f"Failed to load spaCy model: {e}")
#     raise

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test():
    return "this"
@app.post("/cloak")
async def cloak(data: MessageRequest):
    """Endpoint to detect PII in text."""
    input_text = data.message
    if not input_text:
        raise HTTPException(status_code=400, detail="No message provided")

    logging.info("Detect request received!")
    print("Detect request received!")
    return StreamingResponse(
        get_response_stream(global_base_model, system_prompts["detect"], input_text, True),
        media_type="application/json"
    )

@app.post("/cloak_pdf")
async def cloak_pdf(file: UploadFile = File(...)):
    """Endpoint to anonymize PDF files."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        input_pdf_path = temp_pdf.name

    output_dir = Path("redacted_files")
    output_dir.mkdir(exist_ok=True)
    output_pdf_path = output_dir / f"redacted_{file.filename}"

    try:
        result_path = anonymize_pdf(input_pdf_path, output_pdf_path)
        if not result_path or not os.path.exists(result_path):
            raise HTTPException(status_code=500, detail="Failed to process PDF")

        return FileResponse(result_path, filename=f"redacted_{file.filename}", media_type="application/pdf")

    finally:
        os.remove(input_pdf_path)

@app.post("/abstract")
async def abstract(data: MessageRequest):
    """Endpoint to abstract detected PII in text."""
    input_text = data.message
    if not input_text:
        raise HTTPException(status_code=400, detail="No message provided")

    log_to_file("Abstract request received!")

    return StreamingResponse(
        get_response_stream(global_base_model, system_prompts["abstract"], input_text, False),
        media_type="application/json"
    )


# Background initialization
#threading.Thread(target=run_async_in_thread, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port,log_level="debug")
