from app import app, vercel_handler

def handler(request):
    # Convert Vercel request to Flask request
    from flask import Request
    from werkzeug.wrappers import Request as WerkzeugRequest
    
    # Create a test request context
    with app.test_request_context(
        path=request.get('path', '/'),
        method=request.get('httpMethod', 'GET'),
        headers=request.get('headers', {}),
        query_string=request.get('queryStringParameters', {}),
        json=request.get('body')
    ):
        return vercel_handler(request)
