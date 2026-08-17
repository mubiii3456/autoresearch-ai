from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.researcher import researcher_agent
from app.agents.critic import critic_agent

MAX_RETRIES = 3


def research_node(state: AgentState) -> AgentState:
    print(f"\n--- Attempt {state['attempts'] + 1} ---")
    print("Researcher agent is processing...")

    finding = researcher_agent(state["query"], state["rejected_claims"])
    print(f"Researcher output: {finding.claim} (confidence: {finding.confidence})")

    state["finding"] = finding
    state["attempts"] += 1
    return state


def critic_node(state: AgentState) -> AgentState:
    print("Critic agent is validating...")

    feedback = critic_agent(state["finding"])
    print(f"Critic decision: {feedback.approved} | Reason: {feedback.reason}")

    state["feedback"] = feedback
    if feedback.approved:
        state["verified_findings"].append(state["finding"])
    else:
        state["rejected_claims"].append(state["finding"].claim)

    return state


def route_after_critic(state: AgentState) -> str:
    if state["feedback"].approved:
        return "approved"
    if state["attempts"] >= MAX_RETRIES:
        return "max_retries"
    return "retry"


graph = StateGraph(AgentState)
graph.add_node("research", research_node)
graph.add_node("critic", critic_node)

graph.set_entry_point("research")
graph.add_edge("research", "critic")

graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "approved": END,
        "retry": "research",
        "max_retries": END
    }
)

app = graph.compile()


def run_research(query: str):
    print(f"Supervisor: Query received -> '{query}'")

    initial_state: AgentState = {
        "query": query,
        "finding": None,
        "feedback": None,
        "attempts": 0,
        "rejected_claims": [],
        "verified_findings": []
    }

    result = app.invoke(initial_state)

    if result["feedback"].approved:
        print("\nFinal Result:")
        print(f"Claim: {result['finding'].claim}")
        print(f"Source: {result['finding'].source}")
    else:
        print("\nMax retries reached. Escalating to human review.")

    return result


if __name__ == "__main__":
    run_research("What is the current population of Pakistan?")