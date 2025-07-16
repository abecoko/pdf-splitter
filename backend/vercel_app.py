from main import app

# Vercel handler
def handler(request, response):
    return app