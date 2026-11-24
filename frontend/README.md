# Run and publish taskManager

This frontend uses plain HTML, CSS and JavaScript. It needs no npm installation or build step. It starts with an empty result panel, as in the reference sketch. Create opens a form; List fetches tasks; Complete lists unfinished tasks; Delete lists tasks and asks before deleting. No sample data is presented as real data.

## Architecture and choice

Browser → Lambda Function URL → app.lambda_handler → DynamoDB.
Amplify Hosting serves the HTML/CSS/JS to the browser. The browser then calls the separate API URL with POST JSON.

Use **Lambda Function URL + Amplify Hosting** for this small learning demo. Function URLs expose the existing function without configuring API Gateway routes. Amplify provides managed HTTPS hosting and a deployment URL. You do not need Amplify backend libraries or a React build. React would be reasonable as the interface grows, but adds dependencies without much benefit for these four actions.

S3 static website hosting is another option, but its website endpoint does not support HTTPS; a typical HTTPS setup adds CloudFront. A Function URL is the API endpoint, not the static website host. API Gateway becomes useful when you want routes and JWT authentication.

**Access model:** the NONE authentication option below makes the task API public. Anyone who knows its URL can read, create, complete and delete tasks. CORS only governs browsers; it is not authentication. Use disposable demo tasks. For personal/private or multi-user tasks, add sign-in (for example Cognito), API Gateway JWT authorization, and enforce task ownership in the backend before publishing. Never put AWS keys in frontend files. Hosting the frontend privately does not secure a public API.

## 1. Update the existing Lambda

1. Open the existing function in the AWS Lambda console, in the region containing your DynamoDB table.
2. Upload/copy the updated root `app.py`, then choose **Deploy**. Keep the runtime handler set to `app.lambda_handler` (if you use a different filename, change the module part accordingly).
3. Keep environment variable `TASKS_TABLE` set to your table name. Its partition key must be String `task_id`.
4. Keep the execution role's table-scoped permissions for `dynamodb:PutItem`, `Scan`, `UpdateItem`, and `DeleteItem`.
5. Run a direct test event `{"action":"list"}`. You should receive statusCode 200 and a tasks array.

The code does not create an endpoint. AWS config creates it. The new adapter accepts HTTP POST requests and returns a JSON **string** body with the proper status and Content-Type. Direct Lambda tests still return an object body. HTTP failures are logged in CloudWatch without exposing exception details to browsers.

## 2. Create the API endpoint

1. In Lambda, open **Configuration → Function URL → Create function URL**.
2. For this public demo, choose auth type **NONE**. The console creates the required resource-based permissions. Current Function URL access requires both `lambda:InvokeFunctionUrl` and `lambda:InvokeFunction`; see the AWS access-control documentation below if you receive 403.
3. Enable CORS. Set allowed origins to `http://localhost:8000`, allowed methods to `POST`, and allowed headers to `content-type`. Leave credentials disabled. Lambda handles browser OPTIONS preflight for you.
4. Save, and copy the HTTPS Function URL.
5. Paste it into `frontend/config.js` as `apiUrl`. Keep the trailing slash if present.

Configure CORS on the Function URL only; the handler intentionally does not duplicate those headers.

## 3. Try it locally

From the repository root:

```powershell
python -m http.server 8000 --directory frontend
```

Open http://localhost:8000. Use this exact host because CORS distinguishes localhost from 127.0.0.1. Stop the server with Ctrl+C.

Try Create → List tasks → Complete → List tasks → Delete using a disposable task. Changes go to the real DynamoDB table. Without an API URL the page still opens, but actions show a configuration message.

## 4. Publish with Amplify Hosting

1. Package the four website files from the repository root:

```powershell
Compress-Archive -Path frontend/index.html,frontend/styles.css,frontend/app.js,frontend/config.js -DestinationPath "$env:TEMP/taskManager-frontend.zip" -Force
```

2. Open AWS Amplify → **Create new app** → **Deploy without Git** (manual deployment).
3. Enter an app name (for example `taskManager`) and branch name (`main`). Upload the ZIP and deploy. `index.html` must be at the root of the ZIP, not inside a frontend folder.
4. Copy the HTTPS website address Amplify provides.
5. Back in Lambda Function URL CORS settings, add that exact website **origin**, e.g. `https://main.example.amplifyapp.com`, with no trailing slash or path. Keep localhost if you still develop locally.
6. Open the hosted website and repeat the disposable-task check. If you later change config.js or other files, create a fresh ZIP and redeploy.

No AWS infrastructure has been created by these repository changes. Hosting and Lambda/DynamoDB usage can incur AWS charges.

## Troubleshooting

- **API not configured:** fill in config.js, refresh, and redeploy if hosted. “API configured” means the URL is present, not that connectivity was verified.
- **Could not reach API:** check the endpoint, allowed origin/method/header, and browser Network panel. A timed-out change may have succeeded; list tasks before retrying.
- **403:** check Function URL authentication and resource-based permissions. AWS_IAM requires signed requests; this frontend does not sign requests.
- **500:** inspect Lambda CloudWatch logs; check TASKS_TABLE, region, and execution-role permissions.
- **Unreadable response / 502:** deploy the updated app.py and verify the runtime handler.
- **List is empty:** verify you are invoking the expected function and table.

## AWS references

- Function URL creation and CORS: https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html
- Function URL access control: https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html
- Request and response format: https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html
- Amplify manual deployment: https://docs.aws.amazon.com/amplify/latest/userguide/manual-deploys.html
- S3 website endpoints: https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteEndpoints.html

