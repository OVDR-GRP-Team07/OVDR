"""
Main Entry Point for OVDR Backend
Author: Zixin Ding

This script starts the Flask development server. It imports the app factory from the backend package,
initializes the Flask app, and optionally runs cleanup logic upon shutdown.
"""

import atexit
import sys

# Ensure backend package is importable from root directory
sys.path.append("./backend")

# Import the Flask application factory
from backend import create_app

# Create the app instance
app = create_app()

# Register exit hook for graceful shutdow
@atexit.register
def goodbye():
    print("Flask is shutting down.")

# Run the app when executing directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

