import subprocess
import os
import sys
import time
import logging
import argparse
import socket
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Header
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import ollama
import tempfile
import json
import os
import time
from asyncio import run, ensure_future, gather
from pathlib import Path
from cloaking.presidio_requests import  anonymize_text_post,anonymize_pdf_results
from cloaking.presidio import PresidioAnonymizer
from cloaking.llm import LLMAnonymizer
from utils.requests.message_request import MessageRequest,WordListRequest
from utils.constants.vars import  UPLOAD_DIR, global_base_model

"""
SETUP - brew install poppler
brew install tesseract
"""
process = None 
parser = argparse.ArgumentParser(description="Local LLM Server")
parser.add_argument("--port", type=int, default=8000, help="Port for server")
parser.add_argument("--model", type=str, default=global_base_model, help="Model name to use")
args = parser.parse_args()
global_base_model = args.model
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
# Set the model directory
if hasattr(sys, '_MEIPASS'):  # PyInstaller packaged environment
        base_path = sys._MEIPASS
else:
        base_path = os.path.dirname(os.path.abspath(__file__))
os.environ["OLLAMA_MODELS"] = os.path.join(base_path,"models")
print("models path",os.environ["OLLAMA_MODELS"])
logging.info(os.path.abspath("./models"))
# Path to log file
log_file_path = Path("logs.txt")


def getAnonymizerService(use_llm=False):
    if use_llm:
        return LLMAnonymizer(base_model=global_base_model)
    else:
        return PresidioAnonymizer()

anonymizer_service = getAnonymizerService(True)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0
def start_ollama_server():
    
   #Find bin directory
    if hasattr(sys, '_MEIPASS'):  # PyInstaller packaged environment
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(base_path,"ollama","bin")
    ollama_path = os.path.join(bin_dir, "ollama")
    logging.debug(f"Ollama path: {ollama_path}")

    # Verify ollama binary
    if not os.path.exists(ollama_path):
        logging.error(f"Ollama binary not found at {ollama_path}")
        sys.exit(1)
    if not os.access(ollama_path, os.X_OK):
        logging.debug(f"Setting executable permissions for {ollama_path}")
        os.chmod(ollama_path, 0o755)

    # Prepare environment
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    logging.debug(f"Updated PATH: {env['PATH']}")

    # Start Ollama server from bin directory
    try:
        # Free port 11434
        if is_port_in_use(11434):
            logging.warning("Port 11434 is in use, attempting to free it")
            subprocess.run(["pkill", "-f", "ollama"], check=False)
            time.sleep(1)

        process = subprocess.Popen(
            ["ollama", "serve"],
            cwd=bin_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        logging.info("Starting Ollama server...")

        # Monitor output asynchronously
        def read_pipe(pipe, log_func):
            while True:
                line = pipe.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    log_func(line.strip())

        import threading
        threading.Thread(target=read_pipe, args=(process.stdout, logging.debug), daemon=True).start()
        threading.Thread(target=read_pipe, args=(process.stderr, logging.error), daemon=True).start()

        # Wait for server to be ready
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                import requests
                response = requests.get("http://localhost:11434", timeout=1)
                if response.status_code == 200:
                    logging.info("Ollama server ready")
                    break
            except requests.ConnectionError:
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logging.error(f"Ollama process exited. stdout: {stdout}, stderr: {stderr}")
                    sys.exit(1)
                time.sleep(1)
        else:
            logging.error("Ollama failed to start after 20 seconds")
            process.terminate()
            stdout, stderr = process.communicate()
            logging.error(f"Ollama stdout: {stdout}")
            logging.error(f"Ollama stderr: {stderr}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Ollama startup error: {e}")
        if 'process' in locals():
            process.terminate()
        sys.exit(1)

           
async def initialize_server(test_message: str):
    """Initialize the model on startup."""
    try:
        # Consume the async generator using async for
        async for _ in anonymizer_service.anonymize_text(test_message):
            pass  # You don't need to store the result, just need to consume it
        print("Server initialized successfully!")
    except Exception as e:
        print(f"Error initializing server: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("App is starting...")
    print("starting")
    try:
        start_ollama_server()
        await initialize_server("Hi, welcome to Cloak!")
        yield
    finally:
        if process:
            process.terminate()
            logging.info("Ollama server terminated.")
        logging.info("App is shutting down...")

app = FastAPI(lifespan=lifespan)



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
    system_prompt_detect = None
    if data.system_prompts is not None:
       
        try:
            #print(data.system_prompts.detect)
            system_prompt_detect = data.system_prompts.detect
            print(system_prompt_detect)
        except json.JSONDecodeError as e:
            print(e)
            raise HTTPException(status_code=400, detail="Invalid JSON format in body")
    logging.info("Detect request received!")
    print("Detect request received!")
   
    return StreamingResponse(
     
        anonymizer_service.anonymize_text(input_text, system_prompt = system_prompt_detect),
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

    # input_text = anonymizer_service.get_pdf_text(input_pdf_path)
    # print("INPUT", input_text)
   
    return StreamingResponse(
        anonymizer_service.anonymize_pdf(input_pdf_path,"",fill=(0,0,0)),
        media_type="application/json"
    )

@app.post("/redact_pdf")
async def redact_pdf(file: UploadFile = File(...),words_request: str = Form(...)):
    """Endpoint to anonymize PDF files."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    logging.info(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        input_pdf_path = temp_pdf.name
    try:
        word_data = WordListRequest.parse_raw(words_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid word list: {e}")

    output_dir = Path("redacted_files")
    output_dir.mkdir(exist_ok=True)
    output_pdf_path = output_dir / f"redacted_{file.filename}"

    try:
      
        result_path,_ = anonymizer_service.redact_pdf(input_pdf_path, output_pdf_path, word_data.words)
        if not result_path or not os.path.exists(result_path):
            raise HTTPException(status_code=500, detail="Failed to process PDF")
        
        return FileResponse(result_path, filename=f"redacted_{file.filename}", media_type="application/pdf")
   
    finally:
        os.remove(input_pdf_path)

@app.post("/underline_pdf")
async def underline_pdf(file: UploadFile = File(...), words_request: str = Form(...) ):
    """Endpoint to anonymize PDF files."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    logging.info(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        input_pdf_path = temp_pdf.name
    try:
        word_data = WordListRequest.parse_raw(words_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid word list: {e}")

    output_dir = Path("redacted_files")
    output_dir.mkdir(exist_ok=True)
    output_pdf_path = output_dir / f"underlined_{file.filename}"

    try:
      
        result_path,_ = anonymizer_service.underline_pdf(input_pdf_path,output_pdf_path,word_data.words)
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

    logging.info("Abstract request received!")

    return StreamingResponse(
        anonymizer_service.anonymize_text(input_text, system_prompt =settings.system_prompts["abstract"]),
        media_type="application/json"
    )
@app.post("/abstract_pdf")
async def abstract(file: UploadFile = File(...)):
    """Endpoint to abstract detected PII in text."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    logging.info(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(await file.read())
        input_pdf_path = temp_pdf.name

    input_text = anonymizer_service.get_pdf_text(input_pdf_path)
    print("INPUT", input_text)
    logging.info("Abstract request received!")

    return StreamingResponse(
        anonymizer_service.anonymize_text(input_text, system_prompt =settings.system_prompts["abstract"]),
        media_type="application/json"
    )

# Background initialization
#threading.Thread(target=run_async_in_thread, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port,log_level="debug")
