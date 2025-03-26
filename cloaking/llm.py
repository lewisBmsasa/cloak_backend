import time
import ollama
import fitz
import logging
import re
import unicodedata
from utils.constants.vars import  base_options, system_prompts, system_prompts_pdf



def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def identify_sensitive_text(text):
    text = preprocess_text(text)
    response = ollama.chat(model="phi3", messages=[
       
         {'role': 'system', 'content': system_prompts["detect"]},
         {"role": "user", "content": text}
        ])
    return response["message"]["content"].split("\n") 
def preprocess_text(text):
    """Clean and normalize text before feeding it into a PII detection model."""
    # Normalize Unicode (fixes encoding issues)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\x20-\x7E\n]", "", text)  # Keeps ASCII printable characters and newlines
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()  # Replaces multiple spaces and newlines with a single space
    
    # Fix common OCR errors (e.g., "l" -> "1", "O" -> "0")
    text = re.sub(r"\b[lI]\d{2,}\b", lambda m: m.group(0).replace("l", "1").replace("I", "1"), text)  # Example heuristic
    
    # Standardize common patterns (optional)
    text = re.sub(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "[REDACTED_SSN]", text)  # Example: SSN masking
    text = re.sub(r"\b\d{10,16}\b", "[REDACTED_ACCOUNT]", text)  # Example: possible account numbers

    return text
def redact_pdf(pdf_path, output_path, sensitive_words):
    doc = fitz.open(pdf_path)
    for page in doc:
        for word in sensitive_words:
            page.search_for(word)  # Find text positions
            for rect in page.search_for(word):
                page.add_redact_annot(rect)  # Add redaction annotation
        page.apply_redactions()
    doc.save(output_path)

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
        raise Exception(status_code=500, detail=f"Model streaming failed: {str(e)}")


async def split_into_chunks(input_text, chunk_size=100):
    """Split a string into chunks of a specific size."""
    words = input_text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

async def get_response_stream(model_name, user_message, chunking):
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
        async for chunk in async_chat_stream(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompts["detect"]},
                {'role': 'user', 'content': prompt_chunk}
            ],
            format="json",
            stream=True,
            options=base_options
        ):
            log_message = f"Result chunk: {chunk} (Time: {time.time() - start_time:.2f}s)"
            logging.info(f"Result chunk: {chunk} (Time: {time.time() - start_time:.2f}s)")
            yield chunk
           