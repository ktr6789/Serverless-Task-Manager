# Lambda handler interface

This document describes how to call `lambda_handler` in `app.py` with a JSON event. It reflects the current code, which can be tested in the AWS Lambda console.

## How to send an event

For a direct Lambda test, send one JSON object. The `action` field chooses what the function does.

```json
{
  "action": "create",
  "title": "Learn GitHub Actions"
}
```

The handler returns a Python dictionary with `statusCode` and `body`. In the Lambda console, this is the function's returned value. `statusCode` is an HTTP-style number; when invoking Lambda directly, it does not itself make the invocation an HTTP request.

## Actions

### Create a task

Required: non-empty string `title`. Optional: string `description` (defaults to an empty string).

```json
{
  "action": "create",
  "title": "Learn GitHub Actions",
  "description": "Read the project brief"
}
```

Success: `201`; the returned task contains a generated `task_id`.

```json
{
  "statusCode": 201,
  "body": {
    "message": "Task created successfully",
    "task": {
      "task_id": "generated-id",
      "title": "Learn GitHub Actions",
      "description": "Read the project brief",
      "status": "incomplete"
    }
  }
}
```

Errors: `400` if the title is missing, empty, or not a string; `400` if description is not a string.

### List tasks

No additional fields are required.

```json
{"action": "list"}
```

Success: `200`, with all tasks under `body.tasks`. An empty table returns an empty list.

```json
{
  "statusCode": 200,
  "body": {
    "tasks": []
  }
}
```

### Mark a task complete

Required: non-empty string `task_id` copied from a created task.

```json
{
  "action": "complete",
  "task_id": "generated-id"
}
```

Success: `200`; `body.task.status` is `complete`. A task that does not exist returns `404`.

### Delete a task

Required: non-empty string `task_id` copied from a created task.

```json
{
  "action": "delete",
  "task_id": "generated-id"
}
```

Success: `200`; `body.task` contains the deleted task. A task that does not exist returns `404`.

## Error responses

All handled errors use this shape:

```json
{
  "statusCode": 400,
  "body": {
    "error": "A description of the problem"
  }
}
```

Common status codes:

| Status | Meaning |
| --- | --- |
| `200` | List, complete, or delete succeeded |
| `201` | Task created |
| `400` | Invalid event, action, title, description, or task ID |
| `404` | The requested task ID does not exist |

Only these action values are accepted: `create`, `list`, `complete`, and `delete`.

## Optional API Gateway event format

The handler also accepts an API Gateway-style event whose `body` is a **string containing JSON**:

```json
{
  "body": "{\"action\": \"list\"}"
}
```

This describes an input format the code can parse. The current handler returns `body` as a JSON object, whereas API Gateway's Lambda proxy integration generally expects the response `body` to be a string. The current documented interface is therefore direct Lambda invocation; an HTTP API and an OpenAPI/Swagger specification should be added after the HTTP integration and response format are configured.

## AWS setup the handler expects

- Lambda environment variable `TASKS_TABLE` must contain the DynamoDB table name.
- The table must have a String partition key named `task_id`.
- The Lambda execution role needs permission to read and write that table.
