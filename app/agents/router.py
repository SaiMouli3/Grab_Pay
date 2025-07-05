from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.monitoring_agent import run_validation_agent
from app.agents.failure_detection_agent import run_fraud_detection_agent
from app.agents.recovery_agent import run_recovery_agent

def should_continue_after_validation(state: AgentState):
    """Determines the next step after the validation agent has run."""
    if state.get('is_valid'):
        return "run_fraud_detection_agent"
    return "run_recovery_agent"

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("run_validation_agent", run_validation_agent)
workflow.add_node("run_fraud_detection_agent", run_fraud_detection_agent)
workflow.add_node("run_recovery_agent", run_recovery_agent)

# Set the entrypoint
workflow.set_entry_point("run_validation_agent")

# Add conditional edges
workflow.add_conditional_edges(
    "run_validation_agent",
    should_continue_after_validation,
    {
        "run_fraud_detection_agent": "run_fraud_detection_agent",
        "run_recovery_agent": "run_recovery_agent"
    }
)

workflow.add_edge('run_fraud_detection_agent', 'run_recovery_agent')
workflow.add_edge('run_recovery_agent', END)

# Compile the graph
agentic_system = workflow.compile()
