import requests
import fitz  # PyMuPDF
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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

        return text

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage:
book_url = 'https://www.gutenberg.org/cache/epub/74263/pg74263.txt'  # Plain text URL
# book_url = 'https://example.com/path/to/book.pdf'  # PDF URL

text = process_book_from_url(book_url)
print(text)
