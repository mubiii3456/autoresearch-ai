from app.agents.researcher import researcher_agent
from app.agents.critic import critic_agent

MAX_RETRIES = 3


def run_research(query: str):
    print(f"\nSupervisor: Query received -> '{query}'")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- Attempt {attempt} ---")

        print("Researcher agent is processing...")
        finding = researcher_agent(query)
        print(f"Researcher output: {finding.claim} (confidence: {finding.confidence})")

        print("Critic agent is validating...")
        feedback = critic_agent(finding)

        if feedback.approved:
            print(f"Critic approved. Reason: {feedback.reason}")
            print("\nFinal Result:")
            print(f"Claim: {finding.claim}")
            print(f"Source: {finding.source}")
            return finding
        else:
            print(f"Critic rejected. Reason: {feedback.reason}")
            print("Retrying with feedback...")

    print("\nMax retries reached. Escalating to human review.")
    return None


if __name__ == "__main__":
    run_research("What is the current population of Pakistan?")