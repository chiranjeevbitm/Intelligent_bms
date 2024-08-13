import os
import PyPDF2
from transformers import AutoTokenizer, AutoModelForCausalLM

# Initialize the Llama3 model and tokenizer
model_name = "huggingface/llama3-8gb"  # Use the appropriate model name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_summary(text: str, max_length: int = 150):
    inputs = tokenizer.encode(text, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

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
