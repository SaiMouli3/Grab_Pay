# Self-Healing Agentic Transaction System

This project implements a self-healing agentic system for processing financial transactions using LangChain, LangGraph, and the Gemini API. The system is designed to be resilient and intelligent, capable of validating transactions, detecting fraud, and handling fulfillment automatically.

## Features

- **Agentic Workflow**: Uses a multi-agent system built with LangGraph to orchestrate transaction processing.
- **AI-Powered Decision Making**: Leverages the Gemini Pro model for validation, fraud detection, and resolution.
- **Self-Healing Architecture**: The system is structured around monitoring, failure detection, and recovery agents.
- **FastAPI Endpoint**: Exposes a simple API for processing transactions.
- **Secure Configuration**: Uses a `.env` file to manage the API key securely.

## Project Structure

```
.
├── app
│   ├── agents
│   │   ├── __init__.py
│   │   ├── failure_detection_agent.py
│   │   ├── monitoring_agent.py
│   │   ├── recovery_agent.py
│   │   └── router.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── state.py
│   ├── models
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── main.py
├── .env
├── README.md
├── requirements.txt
└── tests
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd transaction-agent-system
    ```

2.  **Create a `.env` file:**
    Create a `.env` file in the root directory and add your Google API key:
    ```
    GOOGLE_API_KEY="your-google-api-key"
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Start the FastAPI server:**
    Use `uvicorn` to run the application.
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

2.  **Access the API documentation:**
    You can find the interactive API documentation at `http://127.0.0.1:8000/docs`.

## How to Use

Send a `POST` request to the `/process_transaction/` endpoint with the transaction data in the request body.

**Example using `curl`:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/process_transaction/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "captureId": "0x500ae41cbaa5264a3a236a4f3bc68eb0ce77d95456b5f84fa6f2ecd4ad9fec0a",
    "requestId": "0x3c624e524e5ed749d8cca8d6dee5e3c34836aaf0830d6b61395b8655980335f1",
    "chargeId": "0x1b70f07c5c4f726da116b86d6209022a6fd6e7c43f919c85dce45f9be4fad34c",
    "status": "PENDING",
    "amount": {
      "value": 65163,
      "currency": "SGD"
    },
    "metadata": {
      "fulfillmentId": "fulfill_gKzqAQnOgM",
      "reason": "Order fulfillment complete for 0x1b70f07c5c4f726da116b86d6209022a6fd6e7c43f919c85dce45f9be4fad34c"
    },
    "createdAt": "2025-06-30T20:53:06+05:30",
    "updatedAt": "2025-06-30T20:53:06+05:30"
  }'
```

The API will return the final state of the transaction after being processed by the agentic system.
