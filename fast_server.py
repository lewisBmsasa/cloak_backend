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
import json
import os
import time
from asyncio import run, ensure_future, gather
from pathlib import Path
from cloaking.presidio_requests import  anonymize_text_post,anonymize_pdf_results
from cloaking.presidio import anonymize_text, anonymize_pdf
from utils.requests.message_request import MessageRequest
from cloaking.llm import get_response_stream, redact_pdf,identify_sensitive_text,extract_text_from_pdf,preprocess_text
from utils.constants.vars import  UPLOAD_DIR

"""
SETUP - brew install poppler
brew install tesseract
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

           
async def initialize_server(test_message: str):
    """Initialize the model on startup."""
    try:
        # Consume the async generator using async for
        async for _ in get_response_stream(base_model, test_message, True):
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
        get_response_stream(global_base_model, input_text, True),
        media_type="application/json"
    )

@app.post("/cloak_pdf")
async def cloak_pdf(file: UploadFile = File(...)):
    """Endpoint to anonymize PDF files."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    logging.info(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        input_pdf_path = temp_pdf.name

    output_dir = Path("redacted_files")
    output_dir.mkdir(exist_ok=True)
    output_pdf_path = output_dir / f"redacted_{file.filename}"

    try:
        # result_path, analysis_results = anonymize_pdf(input_pdf_path, output_pdf_path)
        # if not result_path or not os.path.exists(result_path):
        #     raise HTTPException(status_code=500, detail="Failed to process PDF")

        #return FileResponse(result_path, filename=f"redacted_{file.filename}", media_type="application/pdf")
        text = extract_text_from_pdf(input_pdf_path)
        
        sensitive_words = identify_sensitive_text(text)
        return sensitive_words
        return JSONResponse( content = sensitive_words, status_code = 200)
    finally:
        os.remove(input_pdf_path)

@app.post("/abstract")
async def abstract(data: MessageRequest):
    """Endpoint to abstract detected PII in text."""
    input_text = data.message
    if not input_text:
        raise HTTPException(status_code=400, detail="No message provided")

    logging.info("Abstract request received!")

    return StreamingResponse(
        get_response_stream(global_base_model, input_text, False),
        media_type="application/json"
    )


# Background initialization
#threading.Thread(target=run_async_in_thread, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port,log_level="debug")
