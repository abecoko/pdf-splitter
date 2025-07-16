import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main import app

# Export for Vercel
def handler(event, context):
    return app(event, context)