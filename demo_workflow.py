import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append('.')

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

# Simplified Transaction Model
@dataclass
class TransactionAmount:
    value: int
    currency: str

@dataclass
class Transaction:
    capture_id: str
    request_id: str
    charge_id: str
    status: str
    amount: TransactionAmount
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

# Simplified State
@dataclass
class AgentState:
    transaction: Transaction
    is_valid: Optional[bool] = None
    is_fraudulent: Optional[bool] = None
    fulfillment_status: Optional[str] = None
    error_message: Optional[str] = None
    history: List[str] = field(default_factory=list)

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_step(step: str, message: str):
    print(f"\n{Color.HEADER}{Color.BOLD}=== {step} ==={Color.ENDC}")
    print(f"{Color.CYAN}{message}{Color.ENDC}")

def print_result(success: bool, message: str):
    color = Color.GREEN if success else Color.RED
    print(f"{color}✓ {message}{Color.ENDC}" if success else f"{color}✗ {message}{Color.ENDC}")

class MockResponse:
    def __init__(self, content):
        self.content = content

def run_validation_agent(state: AgentState) -> AgentState:
    """Simulate validation agent"""
    if state.transaction.status == "FAILED":
        state.is_valid = False
        state.history.append("Validation Agent: Transaction status is FAILED. Marking as invalid.")
    else:
        state.is_valid = True
        state.history.append("Validation Agent: Transaction is valid.")
    return state

def run_fraud_detection_agent(state: AgentState) -> AgentState:
    """Simulate fraud detection agent"""
    if not state.is_valid:
        return state
        
    # Simple fraud detection: high amount or suspicious metadata
    is_fraudulent = (
        state.transaction.amount.value >= 10000 or  # High amount
        state.transaction.metadata.get("device_id", "").startswith("suspicious")  # Suspicious device
    )
    
    state.is_fraudulent = is_fraudulent
    state.history.append(
        f"Fraud Detection Agent: Transaction is {'potentially fraudulent' if is_fraudulent else 'not fraudulent'}."
    )
    return state

def run_recovery_agent(state: AgentState) -> AgentState:
    """Simulate recovery agent"""
    if not state.is_valid:
        state.fulfillment_status = "REJECTED"
        state.history.append("Recovery Agent: Transaction rejected due to validation failure.")
    elif state.is_fraudulent:
        state.fulfillment_status = "FLAGGED_FOR_REVIEW"
        state.history.append("Recovery Agent: Transaction flagged for manual review due to fraud concerns.")
    else:
        state.fulfillment_status = "FULFILLED"
        state.history.append("Recovery Agent: Transaction processed successfully.")
    
    return state

def run_workflow(transaction_data: Dict[str, Any]):
    # Create transaction object
    print_step("1. Creating Transaction", f"Processing transaction: {transaction_data['captureId']}")
    
    try:
        amount = TransactionAmount(
            value=transaction_data['amount']['value'],
            currency=transaction_data['amount']['currency']
        )
        
        transaction = Transaction(
            capture_id=transaction_data['captureId'],
            request_id=transaction_data['requestId'],
            charge_id=transaction_data['chargeId'],
            status=transaction_data['status'],
            amount=amount,
            metadata=transaction_data.get('metadata', {}),
            created_at=transaction_data['createdAt'],
            updated_at=transaction_data['updatedAt']
        )
        print_result(True, "Transaction created successfully")
    except Exception as e:
        print_result(False, f"Failed to create transaction: {str(e)}")
        return None

    # Create initial state
    print_step("2. Initializing Agent State", "Creating initial state for transaction processing")
    initial_state = AgentState(transaction=transaction)
    print_result(True, "Agent state initialized")

    # Run the workflow directly without LangChain for demo purposes
    print_step("3. Starting Transaction Processing", "Running through validation, fraud detection, and recovery agents")
    
    try:
        # Run each agent in sequence
        state = run_validation_agent(initial_state)
        state = run_fraud_detection_agent(state)
        state = run_recovery_agent(state)
        
        print_result(True, "Transaction processing completed")
        return state
    except Exception as e:
        print_result(False, f"Error during transaction processing: {str(e)}")
        return

    # Print final results
    print_step("4. Processing Results", "Transaction processing summary:")
    print(f"{Color.BLUE}• Validation: {'✓ Valid' if final_state['is_valid'] else '✗ Invalid'}")
    print(f"• Fraud Check: {'⚠️ Flagged' if final_state['is_fraudulent'] else '✓ Clean'}")
    print(f"• Status: {final_state['fulfillment_status']}")
    if final_state['error_message']:
        print(f"• Error: {Color.RED}{final_state['error_message']}{Color.ENDC}")
    
    print(f"\n{Color.YELLOW}{Color.BOLD}Processing History:{Color.ENDC}")
    for i, entry in enumerate(final_state['history'], 1):
        print(f"{i}. {entry}")

def create_test_transaction(status: str = "SUCCESS", amount: int = 1000, is_fraudulent: bool = False) -> Dict[str, Any]:
    """Helper function to create test transactions"""
    now = datetime.now(timezone.utc).isoformat()
    metadata = {}
        
    if is_fraudulent:
        metadata.update({
            "ip_address": "192.168.1.100",
            "device_id": "suspicious_device_123",
            "user_agent": "Mozilla/5.0 (compatible; SuspiciousBrowser/1.0)"
        })
    
    # Create a unique ID based on the test case
    test_id = int(datetime.now().timestamp())
    
    return {
        "captureId": f"cap_{test_id}",
        "requestId": f"req_{test_id}",
        "chargeId": f"chg_{test_id}",
        "status": status,
        "amount": {
            "value": amount,
            "currency": "SGD"
        },
        "metadata": metadata,
        "createdAt": now,
        "updatedAt": now
    }

def print_workflow_result(test_case: str, final_state):
    """Print the results of a workflow run"""
    print(f"\n{Color.GREEN}=== {test_case} ==={Color.ENDC}")
    print(f"{Color.CYAN}Transaction ID: {final_state.transaction.capture_id}")
    print(f"Amount: {final_state.transaction.amount.value} {final_state.transaction.amount.currency}")
    print(f"Status: {final_state.transaction.status}")
    print(f"\n{Color.YELLOW}Processing Results:{Color.ENDC}")
    print(f"- Valid: {final_state.is_valid}")
    print(f"- Fraudulent: {final_state.is_fraudulent}")
    print(f"- Fulfillment Status: {final_state.fulfillment_status}")
    
    print(f"\n{Color.YELLOW}Processing History:{Color.ENDC}")
    for i, entry in enumerate(final_state.history, 1):
        print(f"{i}. {entry}")
    print("\n" + "="*80 + "\n")

def main():
    print(f"{Color.HEADER}{Color.BOLD}=== Transaction Agent System Demo ==={Color.ENDC}\n")
    
    # Test Case 1: Valid Transaction
    print(f"{Color.BLUE}{Color.BOLD}Test Case 1: Valid Transaction{Color.ENDC}")
    print("-" * 50)
    valid_tx = create_test_transaction("SUCCESS", 1000)
    final_state = run_workflow(valid_tx)
    if final_state:
        print_workflow_result("Valid Transaction Result", final_state)
    
    # Test Case 2: Failed Transaction
    print(f"{Color.BLUE}{Color.BOLD}Test Case 2: Failed Transaction{Color.ENDC}")
    print("-" * 50)
    failed_tx = create_test_transaction("FAILED", 1000)
    final_state = run_workflow(failed_tx)
    if final_state:
        print_workflow_result("Failed Transaction Result", final_state)
    
    # Test Case 3: Potentially Fraudulent Transaction
    print(f"{Color.BLUE}{Color.BOLD}Test Case 3: Potentially Fraudulent Transaction{Color.ENDC}")
    print("-" * 50)
    fraud_tx = create_test_transaction("SUCCESS", 50000, is_fraudulent=True)
    final_state = run_workflow(fraud_tx)
    if final_state:
        print_workflow_result("Fraudulent Transaction Result", final_state)

if __name__ == "__main__":
    main()
