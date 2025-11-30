from app import app
import json

def handler(event, context):
    with app.test_request_context(
        path=event.get('path', '/'),
        method=event.get('httpMethod', 'GET'),
        headers=event.get('headers', {}),
        query_string=event.get('queryStringParameters', {}),
        data=json.dumps(event.get('body', {})) if event.get('body') else None
    ):
        response = app.full_dispatch_request()
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }