from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GOOGLE_API_KEY, GEMINI_MODEL
from app.core.state import AgentState

prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a transaction fulfillment and resolution expert. Based on the transaction status, your job is to either process the fulfillment or flag it for manual review. Generate a brief summary of the action taken."),
     ("human", "The transaction has been processed with the following status:\n\nValidation: {validation_status}\nFraud Check: {fraud_status}\n\nProvide a summary of the next steps.")]
)

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY)

recovery_agent = prompt | llm

def run_recovery_agent(state: AgentState) -> AgentState:
    """Runs the recovery agent to handle fulfillment or resolution."""
    if state.get('is_valid') and not state.get('is_fraudulent'):
        # Simulate fulfillment
        state['fulfillment_status'] = 'SUCCESS'
        validation_status = 'Valid'
        fraud_status = 'Not Fraudulent'
    else:
        state['fulfillment_status'] = 'FLAGGED_FOR_REVIEW'
        validation_status = 'Invalid' if not state.get('is_valid') else 'Valid'
        fraud_status = 'Fraudulent' if state.get('is_fraudulent') else 'Not Fraudulent'

    response = recovery_agent.invoke({
        "validation_status": validation_status,
        "fraud_status": fraud_status
    })

    summary = response.content.strip()
    history_message = f"Recovery Agent: {summary}"
    state['history'].append(history_message)

    return state
