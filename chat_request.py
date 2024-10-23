import os
import time
from typing import Optional, Dict, Any
import json
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, APIConnectionError, BadRequestError

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Constants for retry logic and timeouts
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1
MAX_RETRY_DELAY = 8
REQUEST_TIMEOUT = 30  # seconds

def validate_json_response(content: str) -> Dict[str, Any]:
    """Validate that the response is proper JSON and has expected structure."""
    try:
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Response is not a JSON object")
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")

def send_openai_request(prompt: str, retries: int = MAX_RETRIES) -> str:
    """
    Send a request to OpenAI API with retry logic, fallback models, and enhanced error handling.
    
    Args:
        prompt: The prompt to send to OpenAI
        retries: Number of retries remaining
    
    Returns:
        Validated JSON response as a string
    
    Raises:
        ValueError: If the response is invalid or empty
        Exception: For other API-related errors after all retries are exhausted
    """
    retry_delay = INITIAL_RETRY_DELAY
    models = ["gpt-4", "gpt-3.5-turbo"]  # Fallback model hierarchy
    
    while retries >= 0:
        for model in models:
            try:
                start_time = time.time()
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=REQUEST_TIMEOUT
                )
                
                # Check for timeout
                if time.time() - start_time > REQUEST_TIMEOUT:
                    raise APITimeoutError("Request timeout exceeded")
                
                # Extract content from response
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("OpenAI returned an empty response")
                
                # Validate JSON response
                validate_json_response(content)
                return content
                
            except BadRequestError as e:
                if "model" in str(e).lower():
                    # Model-specific error, try next model
                    continue
                raise ValueError(f"Invalid request parameters: {str(e)}")
                
            except RateLimitError:
                if retries > 0:
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
                    retries -= 1
                    break  # Try again with same model
                raise ValueError("Rate limit exceeded and max retries reached")
                
            except APITimeoutError:
                if retries > 0:
                    time.sleep(1)  # Short delay for timeout
                    retries -= 1
                    break
                raise ValueError("API request timed out and max retries reached")
                
            except APIConnectionError:
                if retries > 0:
                    time.sleep(2)  # Longer delay for connection issues
                    retries -= 1
                    break
                raise ValueError("Failed to connect to OpenAI API after multiple attempts")
                
            except APIError as e:
                if retries > 0 and e.status_code in {500, 502, 503, 504}:
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
                    retries -= 1
                    break
                raise ValueError(f"OpenAI API error: {str(e)}")
                
            except Exception as e:
                raise ValueError(f"Unexpected error while calling OpenAI API: {str(e)}")
        
        retries -= 1
    
    raise ValueError("Maximum retries reached without successful response")
