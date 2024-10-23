from chat_request import send_openai_request
import json

def generate_email_from_task(task: str, recipient_name: str) -> dict:
    """Generate a professional email based on the task description."""
    prompt = f"""
    Generate a professional email based on the following task and recipient.
    Task: {task}
    Recipient Name: {recipient_name}

    Please generate a JSON response with the following structure:
    {{
        "subject": "Email subject line",
        "body": "Email body content with proper greeting and closing",
        "tone": "The overall tone of the email (formal/informal/neutral)"
    }}
    
    Make sure the email is professional, concise, and clearly communicates the task.
    """
    
    try:
        response = send_openai_request(prompt)
        return json.loads(response)
    except Exception as e:
        raise ValueError(f"Failed to generate email: {str(e)}")
