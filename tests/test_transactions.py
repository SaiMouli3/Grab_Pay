import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_process_valid_transaction():
    """
    Tests the processing of a valid transaction.
    """
    transaction_data = {
        "captureId": "0x500ae41cbaa5264a3a236a4f3bc68eb0ce77d95456b5f84fa6f2ecd4ad9fec0a",
        "requestId": "0x3c624e524e5ed749d8cca8d6dee5e3c34836aaf0830d6b61395b8655980335f1",
        "chargeId": "0x1b70f07c5c4f726da116b86d6209022a6fd6e7c43f919c85dce45f9be4fad34c",
        "status": "FAILURE",
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
    }
    response = client.post("/process_transaction/", json=transaction_data)
    assert response.status_code == 200
    result = response.json()
    # Because the LLM response can be unpredictable, we will just check the status code
    # and that the history has been populated.
    assert len(result['history']) > 0
