from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GOOGLE_API_KEY, GEMINI_MODEL
from app.core.state import AgentState


prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a transaction validation expert. Your task is to validate the provided transaction data. 
    Check for the following:
    1. Required fields are present (captureId, requestId, chargeId, status, amount, metadata)
    2. Status must be one of: PENDING, SUCCESS, FAILED
    3. Amount must be a positive number
    4. Currency must be a valid 3-letter currency code
    5. Timestamps must be valid ISO 8601 format
    
    Respond with only 'yes' if all validations pass, otherwise 'no'.
    """),
    ("human", """Here is the transaction data:
    
    {transaction_json}
    
    Based on the validation rules, is this transaction valid? Respond with only 'yes' or 'no'.""")
])

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY)

validation_agent = prompt | llm

def run_validation_agent(state: AgentState) -> AgentState:
    """Runs the validation agent to check the transaction data."""
    # First check the status field immediately
    if state['transaction'].status == 'FAILURE':
        state['is_valid'] = False
        state['error_message'] = "Transaction status is FAILURE. Marking as invalid."
        state['history'].append("Validation Agent: Transaction status is FAILURE. Marking as invalid.")
        return state
        
    # If status is not FAILURE, proceed with full validation
    transaction_json = state['transaction'].model_dump_json(indent=2)
    response = validation_agent.invoke({"transaction_json": transaction_json})
    
    is_valid = response.content.strip().lower() == 'yes'
    state['is_valid'] = is_valid
    
    history_message = f"Validation Agent: Transaction is {'valid' if is_valid else 'invalid'}."
    state['history'].append(history_message)
    
    if not is_valid:
        state['error_message'] = "Transaction failed validation checks."

    return state
