from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GOOGLE_API_KEY, GEMINI_MODEL
from app.core.state import AgentState

prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a fraud detection expert. Your task is to analyze the provided transaction data for any signs of fraudulent activity. Consider factors like transaction amount, frequency, and metadata. Based on your analysis, decide if the transaction is fraudulent. Respond with only 'yes' or 'no'."),
     ("human", "Here is the transaction data:\n\n{transaction_json}")]
)

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY)

fraud_detection_agent = prompt | llm

def run_fraud_detection_agent(state: AgentState) -> AgentState:
    """Runs the fraud detection agent to analyze the transaction."""
    transaction_json = state['transaction'].model_dump_json(indent=2)
    response = fraud_detection_agent.invoke({"transaction_json": transaction_json})
    
    is_fraudulent = response.content.strip().lower() == 'yes'
    state['is_fraudulent'] = is_fraudulent
    
    history_message = f"Fraud Detection Agent: Transaction is {'fraudulent' if is_fraudulent else 'not fraudulent'}."
    state['history'].append(history_message)
    
    if is_fraudulent:
        state['error_message'] = "Transaction flagged as potentially fraudulent."

    return state
