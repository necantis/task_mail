import os
from app import app

if __name__ == "__main__":
    # Use port 5000 as per Flask website blueprint guidelines
    port = int(os.environ.get("PORT", 5000))
    # Run the app with host set to 0.0.0.0 to make it publicly accessible
    app.run(host="0.0.0.0", port=port)
