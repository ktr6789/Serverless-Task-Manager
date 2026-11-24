# Task manager operations for AWS Lambda.

import json
import os
import base64
import binascii
import logging
from uuid import uuid4

def _task_table():
    """Return the DynamoDB table configured for the Lambda function."""
    table_name = os.environ.get('TASKS_TABLE')
    if not table_name:
        raise RuntimeError('TASKS_TABLE environment variable is not configured')

    import boto3

    return boto3.resource('dynamodb').Table(table_name)


def lambda_handler(event, context):
    """Adapt HTTP requests while preserving direct Lambda invocation responses."""
    is_http = isinstance(event, dict) and ('requestContext' in event or 'httpMethod' in event)
    if not is_http:
        return _handle_action(event, context)

    method = event.get('requestContext', {}).get('http', {}).get('method') or event.get('httpMethod')
    if method != 'POST':
        response = {'statusCode': 405, 'body': {'error': 'Use POST with a JSON action'}}
    else:
        try:
            body = event.get('body') or ''
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body, validate=True).decode('utf-8')
            payload = json.loads(body)
        except (ValueError, TypeError, UnicodeError, binascii.Error):
            response = {'statusCode': 400, 'body': {'error': 'Request body must contain valid JSON'}}
        else:
            try:
                response = _handle_action(payload, context)
            except Exception:
                logging.exception('Task request failed')
                response = {'statusCode': 500, 'body': {'error': 'Unable to process the request. Check Lambda logs.'}}
    headers = {'Content-Type': 'application/json', 'Cache-Control': 'no-store'}
    if response['statusCode'] == 405:
        headers['Allow'] = 'POST'
    # Configure CORS on the Function URL (or API Gateway), not in both places.
    return {**response, 'headers': headers, 'body': json.dumps(response['body'])}


def _handle_action(event, context):
    """Handle create, list, complete, and delete JSON events using DynamoDB.

    The table must use a String partition key named ``task_id``.
    """
    if not isinstance(event, dict):
        return {'statusCode': 400, 'body': {'error': 'Event must be a JSON object'}}

    # Support API Gateway proxy events as well as direct Lambda test events.
    if isinstance(event.get('body'), str):
        try:
            event = json.loads(event['body'])
        except json.JSONDecodeError:
            return {'statusCode': 400, 'body': {'error': 'Request body must contain valid JSON'}}
        if not isinstance(event, dict):
            return {'statusCode': 400, 'body': {'error': 'Request body must be a JSON object'}}

    action = event.get('action')
    if not isinstance(action, str) or action not in {'create', 'list', 'complete', 'delete'}:
        return {'statusCode': 400, 'body': {'error': "Invalid action. Use 'create', 'list', 'complete', or 'delete'."}}

    table = _task_table()
    if action == 'create':
        title = event.get('title')
        if not isinstance(title, str) or not title.strip():
            return {'statusCode': 400, 'body': {'error': 'A non-empty title is required'}}
        description = event.get('description', '')
        if not isinstance(description, str):
            return {'statusCode': 400, 'body': {'error': 'Description must be a string'}}
        task = {
            'task_id': str(uuid4()),
            'title': title.strip(),
            'description': description,
            'status': 'incomplete',
        }
        table.put_item(Item=task)
        return {'statusCode': 201, 'body': {'message': 'Task created successfully', 'task': task}}

    if action == 'list':
        result = table.scan()
        items = result.get('Items', [])
        while result.get('LastEvaluatedKey'):
            result = table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
            items.extend(result.get('Items', []))
        items.sort(key=lambda item: item['task_id'])
        return {'statusCode': 200, 'body': {'tasks': items}}

    task_id = event.get('task_id')
    if not isinstance(task_id, str) or not task_id.strip():
        return {'statusCode': 400, 'body': {'error': 'A non-empty task_id is required'}}
    task_id = task_id.strip()

    if action == 'complete':
        try:
            result = table.update_item(
                Key={'task_id': task_id},
                UpdateExpression='SET #status = :complete',
                ConditionExpression='attribute_exists(task_id)',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':complete': 'complete'},
                ReturnValues='ALL_NEW',
            )
        except Exception as error:
            if error.__class__.__name__ == 'ConditionalCheckFailedException':
                return {'statusCode': 404, 'body': {'error': f'Task {task_id} was not found'}}
            raise
        return {'statusCode': 200, 'body': {'message': 'Task marked as complete', 'task': result['Attributes']}}

    try:
        result = table.delete_item(
            Key={'task_id': task_id},
            ConditionExpression='attribute_exists(task_id)',
            ReturnValues='ALL_OLD',
        )
    except Exception as error:
        if error.__class__.__name__ == 'ConditionalCheckFailedException':
            return {'statusCode': 404, 'body': {'error': f'Task {task_id} was not found'}}
        raise
    return {'statusCode': 200, 'body': {'message': 'Task deleted successfully', 'task': result['Attributes']}}
