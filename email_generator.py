from typing import Dict, Optional
import json
from chat_request import send_openai_request, validate_json_response

def validate_email_response(response: Dict) -> None:
    """Validate that the email response contains all required fields."""
    required_fields = {"subject", "body", "tone"}
    missing_fields = required_fields - set(response.keys())
    if missing_fields:
        raise ValueError(f"Missing required fields in email response: {', '.join(missing_fields)}")
    
    if not isinstance(response["subject"], str) or not response["subject"].strip():
        raise ValueError("Email subject is empty or invalid")
    if not isinstance(response["body"], str) or not response["body"].strip():
        raise ValueError("Email body is empty or invalid")
    if not isinstance(response["tone"], str) or not response["tone"].strip():
        raise ValueError("Email tone is empty or invalid")

def generate_email_from_task(task: str, recipient_name: str, max_retries: int = 3) -> Dict:
    """
    Generate a professional email based on the task description.
    
    Args:
        task: The task description
        recipient_name: Name of the email recipient
        max_retries: Maximum number of retries for API calls
    
    Returns:
        Dict containing email subject, body, and tone
    
    Raises:
        ValueError: If the response is invalid or required fields are missing
    """
    if not task or not task.strip():
        raise ValueError("Task description cannot be empty")
    if not recipient_name or not recipient_name.strip():
        raise ValueError("Recipient name cannot be empty")

    prompt = f"""
    Generate a professional email based on the following task and recipient.
    Task: {task}
    Recipient Name: {recipient_name}

    Return a JSON response with exactly this structure:
    {{
        "subject": "Clear and concise email subject line",
        "body": "Professional email body with proper greeting and closing",
        "tone": "The overall tone of the email (formal/informal/neutral)"
    }}
    
    Requirements:
    1. Subject should be clear and related to the task
    2. Body must include proper greeting and professional closing
    3. Tone should match the task's nature and recipient
    4. Use professional language and proper formatting
    """
    
    try:
        # Get response from OpenAI
        response_str = send_openai_request(prompt, retries=max_retries)
        
        # Parse and validate response
        response = json.loads(response_str)
        validate_email_response(response)
        
        return response
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse email generation response: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to generate email: {str(e)}")
