from app import app

def handler(request):
    return app.vercel_handler(request, None)
