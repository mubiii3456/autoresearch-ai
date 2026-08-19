from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.agents.researcher import researcher_agent
from app.agents.critic import critic_agent
from app.mcp_clients.storage_client import save_report
from app.memory.cache import get_cached_result, set_cached_result
from app.agents.writer import writer_agent
from app.agents.editor import editor_agent

STEP_LABELS = {
    "research": "Researcher agent is searching and analyzing...",
    "critic": "Critic agent is validating the finding...",
    "writer": "Writer agent is drafting the report...",
    "editor": "Editor agent is polishing the final report..."
}

MAX_RETRIES = 3


def research_node(state: AgentState) -> AgentState:
    print(f"\n--- Attempt {state['attempts'] + 1} ---")
    print("Researcher agent is processing...")

    result = researcher_agent(state["query"], state["rejected_claims"])

    if result["needs_clarification"]:
        print(f"Researcher needs clarification: {result['question']}")
        state["needs_clarification"] = True
        state["clarification_question"] = result["question"]
        state["total_tokens"] += result["tokens"]
        state["total_cost"] += result["cost"]
        return state

    finding = result["finding"]
    print(f"Researcher output: {finding.claim} (confidence: {finding.confidence})")

    state["finding"] = finding
    state["needs_clarification"] = False
    state["attempts"] += 1
    state["total_tokens"] += result["tokens"]
    state["total_cost"] += result["cost"]
    return state


def critic_node(state: AgentState) -> AgentState:
    print("Critic agent is validating...")

    feedback, tokens, cost = critic_agent(state["finding"])
    state["total_tokens"] += tokens
    state["total_cost"] += cost
    print(f"Critic decision: {feedback.approved} | Reason: {feedback.reason}")

    state["feedback"] = feedback

    if feedback.approved:
        state["verified_findings"].append(state["finding"])
    else:
        state["rejected_claims"].append(state["finding"].claim)

    return state


def writer_node(state: AgentState) -> AgentState:
    print("Writer agent is drafting report...")

    draft, tokens, cost = writer_agent(state["query"], state["finding"].claim, state["finding"].source)
    state["total_tokens"] += tokens
    state["total_cost"] += cost
    print(f"Draft: {draft}")

    state["draft_report"] = draft
    return state


def editor_node(state: AgentState) -> AgentState:
    print("Editor agent is polishing report...")

    final, tokens, cost = editor_agent(state["draft_report"], state["finding"].source)
    state["total_tokens"] += tokens
    state["total_cost"] += cost
    print(f"Final report: {final}")

    state["final_report"] = final
    return state


def route_after_research(state: AgentState) -> str:
    if state["needs_clarification"]:
        return "needs_clarification"
    return "proceed_to_critic"


def route_after_critic(state: AgentState) -> str:
    if state["feedback"].approved:
        return "approved"
    if state["attempts"] >= MAX_RETRIES:
        return "max_retries"
    return "retry"


graph = StateGraph(AgentState)
graph.add_node("research", research_node)
graph.add_node("critic", critic_node)
graph.add_node("writer", writer_node)
graph.add_node("editor", editor_node)

graph.set_entry_point("research")

graph.add_conditional_edges(
    "research",
    route_after_research,
    {
        "needs_clarification": END,
        "proceed_to_critic": "critic"
    }
)

graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "approved": "writer",
        "retry": "research",
        "max_retries": END
    }
)

graph.add_edge("writer", "editor")
graph.add_edge("editor", END)

app = graph.compile()

def build_initial_state(query: str) -> AgentState:
    return {
        "query": query,
        "finding": None,
        "feedback": None,
        "attempts": 0,
        "rejected_claims": [],
        "verified_findings": [],
        "needs_clarification": False,
        "clarification_question": None,
        "draft_report": None,
        "final_report": None,
        "total_tokens": 0,
        "total_cost": 0.0
    }

def run_research(query: str):
    print(f"Supervisor: Query received -> '{query}'")

    cached = get_cached_result(query)
    if cached:
        print(f"\nCache hit! Returning cached result.")
        print(f"Claim: {cached['claim']}")
        print(f"Source: {cached['source']}")
        return cached

    initial_state = build_initial_state(query)

    result = app.invoke(initial_state)

    if result["needs_clarification"]:
        print(f"\nClarification needed: {result['clarification_question']}")
    elif result["feedback"].approved:
        print("\nFinal Polished Report:")
        print(result["final_report"])

        saved = save_report(result["query"], result["finding"].claim, result["finding"].source)
        print(f"\nReport saved with ID: {saved['report_id']}")
        set_cached_result(result["query"], result["finding"].claim, result["finding"].source, result["finding"].confidence)
    else:
        print("\nMax retries reached. Escalating to human review.")

    return result

def run_until_critic(query: str):
    state = build_initial_state(query)

    for attempt in range(1, 4):
        state = research_node(state)
        if state["needs_clarification"]:
            return state
        state = critic_node(state)
        if state["feedback"].approved:
            return state
        if state["attempts"] >= 3:
            return state

    return state


def run_writer_editor(state: AgentState):
    state = writer_node(state)
    state = editor_node(state)
    return state

if __name__ == "__main__":
    run_research("What is the current population of Pakistan?")