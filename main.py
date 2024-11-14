import os
import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Use Replit's default port (8080)
        port = int(os.environ.get("PORT", "8080"))
        logger.info(f"Starting server on port {port}")
        
        # Run the app with host set to 0.0.0.0 to make it publicly accessible
        app.run(host="0.0.0.0", port=port)
    except ValueError as e:
        logger.error(f"Invalid port configuration: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)
