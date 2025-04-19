import logging
from application import app as application

# Configure logging at the root level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a reference to the application for Gunicorn
app = application