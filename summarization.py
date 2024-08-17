# summarization.py
import os
from pdfminer.high_level import extract_text
import torch
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
    # Implement downloading book from URL and extracting text
    pass

def generate_summary(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    summary_ids = pipeline_model.model.generate(inputs.input_ids, max_length=summary_length, num_beams=5, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
