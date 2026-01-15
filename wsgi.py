"""
WSGI entry point for production deployment (Railway, Heroku, etc.)
"""
import sys
import os

# Add the src directory to Python path so 'app' module can be found
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Now import the Flask app
from app.web.server import app as application

# For gunicorn compatibility
app = application

if __name__ == '__main__':
    application.run()
