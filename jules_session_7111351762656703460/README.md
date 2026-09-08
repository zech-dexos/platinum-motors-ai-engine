# Platinum Motors AI Engine

A custom dealership AI sales and inventory management backend built with Python and FastAPI. It is designed to power a 24/7 intelligent lead capture agent and manage a local inventory of up to 37 cars.

## Features

- **Inventory Management**: Manages vehicles with distinct statuses ("In Stock", "Coming Soon", "Sold").
- **Multi-format Ingestion**: Parse inventory feeds from CSV, JSON, and XML using `parser.py`.
- **Manual Intake**: Instantly push raw text/specs for "Coming Soon" arrivals into memory.
- **FastAPI Backend**: Provides a robust, fully asynchronous API for searches and management.
- **Chat Agent Endpoint**: Endpoint designed for LLM integration to handle lead capture and test drive bookings.

## Requirements

Ensure you have Python 3.9+ installed. Dependencies are listed in `requirements.txt`.

Install them using:
```bash
pip install -r requirements.txt
```

## Running the Server Locally

You can run the application locally using Uvicorn. The server will hot-reload on code changes.

```bash
uvicorn api:app --reload
```

The server will be available at `http://127.0.0.1:8000`.
You can access the automatic interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## Inventory Sync Operations

Inventory parsing logic is housed in `parser.py`. You can utilize the functions `parse_csv`, `parse_json`, `parse_xml`, and `parse_remote_json` to read structured files or remote endpoints and map them into strict Pydantic `Vehicle` models.

To manually provision a "Coming Soon" car when photos or full data are not yet available, utilize the manual intake fallback function (`manual_intake` in `parser.py` or the `POST /intake/manual` endpoint) using basic raw specs.

## Environment Configuration

When deploying this application to a cloud provider like Railway or Docker, you can set the following environment variables (though none are strictly required for the basic scaffolding):

- `HOST`: Set to `0.0.0.0` for Docker/cloud deployments.
- `PORT`: Define the port to listen on (e.g., 8000).
- `OPENAI_API_KEY`: If implementing the real LLM logic in the `/chat/agent` endpoint using the included `openai` dependency.

For a Dockerized deployment, a simple `Dockerfile` could look like:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```
