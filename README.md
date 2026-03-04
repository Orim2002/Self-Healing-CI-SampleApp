# Self-Healing CI — Sample App

A minimal Flask application used to test and demonstrate the self-healing pipeline. It exposes a `/health` endpoint that the watchdog monitors, and `/fail` and `/recover` endpoints to simulate failures on demand.

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Returns service status and request metrics. Returns 200 when healthy, 503 when in failure mode. |
| `GET /fail` | Activates failure mode. All subsequent `/health` checks return 503. |
| `GET /recover` | Restores normal operation. |

### Health response

```json
{
  "status": "healthy",
  "total_requests": 142,
  "error_rate": 0.0
}
```

The watchdog reads `total_requests` and `error_rate` from this response to track whether the deployment is safe to use as a rollback target.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

The app listens on port 8080.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

Tests cover the three main behaviors: healthy responses, failure mode activation, and recovery.

## CI/CD

Pushing to `master` triggers the GitHub Actions pipeline, which runs tests, builds a Docker image, pushes it to ECR, and triggers a Jenkins deployment via HTTPS API.

The pipeline requires the following GitHub secrets and variables:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `JENKINS_TOKEN`
- `AWS_REGION` (variable)
- `JENKINS_URL` (variable)
- `JENKINS_USER` (variable)

## Testing the self-healing loop

Once deployed to Kubernetes, you can simulate a production failure using port-forward:

```bash
kubectl port-forward deployment/sample-app 9090:8080
curl http://localhost:9090/fail
```

The watchdog will detect 5 consecutive `/health` failures, look up the last safe build in the registry, and trigger a Jenkins rollback job. You should receive a Telegram alert within about a minute.

To check the watchdog logs while this is happening:

```bash
kubectl logs -l app=health-watchdog -f
```