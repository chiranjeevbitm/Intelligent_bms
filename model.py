import os
import PyPDF2
import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# Initialize the text generation pipeline with the Llama3 model
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

def generate_summary(text: str, max_new_tokens: int = 150):
    # Prepare the input as a system message for the model
    messages = [
        {"role": "system", "content": "You are a chatbot that provides concise summaries of book content."},
        {"role": "user", "content": text},
    ]
    
    # Generate summary
    outputs = pipeline(
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    
    # Return the generated summary text
    return outputs[0]["generated_text"]

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfFileReader(file)
            num_pages = reader.numPages
            for page_num in range(num_pages):
                page = reader.getPage(page_num)
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Failed to extract text from {pdf_path}: {e}")
    return text

# Path to the directory containing the PDFs
pdf_directory = "books"  # Change this to your directory path

# Iterate through all PDF files in the directory and generate summaries
for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        print(f"Processing file: {filename}")
        
        # Extract text from the PDF
        book_text = extract_text_from_pdf(pdf_path)
        
        if book_text.strip():  # Ensure that there's text to summarize
            # Generate summary
            summary = generate_summary(book_text)
            print(f"Summary for {filename}:")
            print(summary)
            print("\n" + "="*80 + "\n")
        else:
            print(f"No text found in {filename}")
