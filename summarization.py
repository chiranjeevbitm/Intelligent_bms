# summarization.py
import os
from pdfminer.high_level import extract_text
import torch
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from transformers import AutoTokenizer, pipeline

model_id = "Falconsai/text_summarization"
access_token = "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"
summary_length = 150

pipeline_model = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    token=access_token,
    device="cpu"
)
tokenizer = AutoTokenizer.from_pretrained(model_id, token=access_token)

def process_uploaded_book(book_file):
    text = extract_text(book_file)
    return generate_summary(text)

def process_book_from_url(book_url):
    try:
        # Setup retries for requests
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Fetch the content from the URL
        response = session.get(book_url)
        response.raise_for_status()  # Check if the request was successful

        # Get the content type from headers
        content_type = response.headers.get('Content-Type', '')

        if 'text/plain' in content_type:
            # Handle plain text files
            text = response.text

        else:
            return "Unsupported content type"

        return generate_summary(text)
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

def generate_summary(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    summary_ids = pipeline_model.model.generate(inputs.input_ids, max_length=summary_length, num_beams=5, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
