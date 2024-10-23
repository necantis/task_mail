import PyPDF2
from typing import Dict, List, Optional
import json
from chat_request import send_openai_request, validate_json_response

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

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file with proper error handling."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if not pdf_reader.pages:
            raise ValueError("PDF file appears to be empty")
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No readable text content found in PDF")
        
        return text
    except PyPDF2.PdfReadError as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing PDF file: {str(e)}")

def analyze_document_segment(text_segment: str, max_retries: int = 3) -> Dict:
    """Analyze a segment of text with proper error handling and validation."""
    if not text_segment or not text_segment.strip():
        raise ValueError("Empty text segment provided for analysis")

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
    
    try:
        # Get response from OpenAI
        response_str = send_openai_request(prompt, retries=max_retries)
        
        # Parse and validate response
        response = json.loads(response_str)
        validate_analysis_response(response)
        
        return response
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse analysis response: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to analyze text segment: {str(e)}")

def analyze_pdf_document(pdf_file) -> Dict:
    """Analyze entire PDF document with comprehensive error handling."""
    try:
        text = extract_text_from_pdf(pdf_file)
        
        # Split text into manageable segments (roughly 1000 words each)
        words = text.split()
        if not words:
            raise ValueError("No text content found in PDF")
            
        segment_size = 1000
        segments = [' '.join(words[i:i + segment_size]) 
                   for i in range(0, len(words), segment_size)]
        
        # Analyze each segment
        analysis_results = []
        for segment in segments:
            if segment.strip():
                try:
                    result = analyze_document_segment(segment)
                    analysis_results.append(result)
                except Exception as e:
                    # Log the error but continue with other segments
                    print(f"Warning: Failed to analyze segment: {str(e)}")
                    continue
        
        if not analysis_results:
            raise ValueError("Failed to analyze any segments of the document")
        
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
        
    except Exception as e:
        raise ValueError(f"Failed to analyze PDF document: {str(e)}")
