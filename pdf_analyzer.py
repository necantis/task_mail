import PyPDF2
from chat_request import send_openai_request
import json
from typing import Dict, List

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def analyze_document_segment(text_segment: str) -> Dict:
    """Analyze a segment of text for inconsistencies and logical issues."""
    prompt = f"""
    Analyze the following text segment for inconsistencies, logical fallacies, and unsupported statements.
    Return the analysis in JSON format with the following structure:
    {{
        "inconsistencies": ["List of identified inconsistencies"],
        "logical_fallacies": ["List of logical fallacies found"],
        "unsupported_statements": ["List of statements that lack proper support or evidence"],
        "suggestions": ["List of suggestions for improvement"]
    }}

    Text to analyze:
    {text_segment}
    """
    
    try:
        response = send_openai_request(prompt)
        return json.loads(response)
    except Exception as e:
        raise ValueError(f"Failed to analyze text segment: {str(e)}")

def analyze_pdf_document(pdf_file) -> Dict:
    """Analyze entire PDF document for issues."""
    text = extract_text_from_pdf(pdf_file)
    
    # Split text into manageable segments (roughly 1000 words each)
    words = text.split()
    segment_size = 1000
    segments = [' '.join(words[i:i + segment_size]) 
               for i in range(0, len(words), segment_size)]
    
    # Analyze each segment
    analysis_results = []
    for segment in segments:
        if segment.strip():  # Only analyze non-empty segments
            analysis_results.append(analyze_document_segment(segment))
    
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
