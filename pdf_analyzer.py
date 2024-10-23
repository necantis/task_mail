import os
import PyPDF2
from typing import Dict, List, Optional, Generator
import json
import time
from chat_request import send_openai_request, validate_json_response

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 2000  # words per chunk
MAX_RETRIES = 3
TIMEOUT = 30  # seconds

class PDFAnalysisError(Exception):
    """Custom exception for PDF analysis errors"""
    pass

def validate_analysis_response(response: Dict) -> None:
    """Validate that the analysis response contains all required fields with proper types."""
    required_fields = {
        "inconsistencies": list,
        "logical_fallacies": list,
        "unsupported_statements": list,
        "suggestions": list
    }
    
    for field, expected_type in required_fields.items():
        if field not in response:
            raise ValueError(f"Missing required field in analysis response: {field}")
        if not isinstance(response[field], expected_type):
            raise ValueError(f"Invalid type for field '{field}': expected {expected_type.__name__}")

def check_file_size(file) -> None:
    """Check if file size is within acceptable limits."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise PDFAnalysisError(f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024:.1f}MB")

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file with enhanced error handling."""
    try:
        check_file_size(pdf_file)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if not pdf_reader.pages:
            raise PDFAnalysisError("PDF file appears to be empty")
        
        text = ""
        total_pages = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                raise PDFAnalysisError(f"Error extracting text from page {page_num}: {str(e)}")
        
        if not text.strip():
            raise PDFAnalysisError("No readable text content found in PDF")
        
        return text
    except PyPDF2.PdfReadError as e:
        raise PDFAnalysisError(f"Failed to read PDF file: {str(e)}")
    except Exception as e:
        if isinstance(e, PDFAnalysisError):
            raise
        raise PDFAnalysisError(f"Error processing PDF file: {str(e)}")

def chunk_text(text: str) -> Generator[str, None, None]:
    """Split text into manageable chunks for analysis."""
    words = text.split()
    for i in range(0, len(words), CHUNK_SIZE):
        chunk = ' '.join(words[i:i + CHUNK_SIZE])
        if chunk.strip():
            yield chunk

def analyze_document_segment(text_segment: str, max_retries: int = MAX_RETRIES) -> Dict:
    """Analyze a segment of text with enhanced error handling and timeout."""
    if not text_segment or not text_segment.strip():
        raise PDFAnalysisError("Empty text segment provided for analysis")

    prompt = f"""
    Analyze the following text segment for inconsistencies, logical fallacies, and unsupported statements.
    Return the analysis in JSON format with exactly this structure:
    {{
        "inconsistencies": ["List of identified inconsistencies"],
        "logical_fallacies": ["List of logical fallacies found"],
        "unsupported_statements": ["List of statements that lack proper support or evidence"],
        "suggestions": ["List of suggestions for improvement"]
    }}

    Text to analyze:
    {text_segment}
    """
    
    start_time = time.time()
    try:
        # Get response from OpenAI with timeout
        if time.time() - start_time > TIMEOUT:
            raise PDFAnalysisError("Analysis timeout exceeded")
            
        response_str = send_openai_request(prompt, retries=max_retries)
        
        # Parse and validate response
        response = json.loads(response_str)
        validate_analysis_response(response)
        
        return response
    except json.JSONDecodeError as e:
        raise PDFAnalysisError(f"Failed to parse analysis response: {str(e)}")
    except Exception as e:
        raise PDFAnalysisError(f"Failed to analyze text segment: {str(e)}")

def analyze_pdf_document(pdf_file) -> Dict:
    """Analyze entire PDF document with comprehensive error handling and chunking."""
    try:
        # Extract text with size validation
        text = extract_text_from_pdf(pdf_file)
        
        # Process text in chunks
        analysis_results = []
        failed_chunks = 0
        for chunk in chunk_text(text):
            try:
                result = analyze_document_segment(chunk)
                analysis_results.append(result)
            except Exception as e:
                failed_chunks += 1
                if failed_chunks > MAX_RETRIES:
                    raise PDFAnalysisError("Too many failed analysis attempts")
                continue
        
        if not analysis_results:
            raise PDFAnalysisError("Failed to analyze any segments of the document")
        
        # Combine results
        combined_results = {
            "inconsistencies": [],
            "logical_fallacies": [],
            "unsupported_statements": [],
            "suggestions": []
        }
        
        for result in analysis_results:
            for key in combined_results:
                combined_results[key].extend(result.get(key, []))
        
        # Remove duplicates while preserving order
        for key in combined_results:
            combined_results[key] = list(dict.fromkeys(combined_results[key]))
        
        return combined_results
        
    except PDFAnalysisError:
        raise
    except Exception as e:
        raise PDFAnalysisError(f"Failed to analyze PDF document: {str(e)}")
