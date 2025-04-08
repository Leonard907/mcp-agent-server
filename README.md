# Model Context Protocol Server

A simple implementation of a Model Context Protocol server with a dummy tool.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

The server will start on `http://localhost:8000`

## Available Tools

### Dummy Tool
- Endpoint: `/tools/dummy_tool`
- Method: POST
- Parameters: None
- Returns: Empty string

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
