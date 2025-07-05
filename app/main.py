from fastapi import FastAPI, HTTPException
from app.models.schemas import Transaction
from app.agents.router import agentic_system
from app.core.state import AgentState

app = FastAPI(
    title="Self-Healing Agentic System",
    description="An agentic system for processing transactions with self-healing capabilities.",
    version="1.0.0"
)

@app.post("/process_transaction/", response_model=AgentState)
def process_transaction(transaction: Transaction):
    """
    Receives a transaction, processes it through the agentic workflow,
    and returns the final state.
    """
    initial_state = AgentState(
        transaction=transaction,
        is_valid=None,
        is_fraudulent=None,
        fulfillment_status=None,
        error_message=None,
        history=[]
    )

    try:
        final_state = agentic_system.invoke(initial_state)
        return final_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Self-Healing Agentic System API"}
