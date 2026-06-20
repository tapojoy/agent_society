from typing import Literal
from typing import TypedDict

class InteractionState(TypedDict):
    status: str
    session_id: str
    interaction_no: int
    interaction_id: str
    interaction_type: Literal["formal", "informal"]
    participants: list
    all_agents: list
    domain: str
    topic: str
    topic_initiator: str | None
    pro_agent: str | None
    con_agent: str | None
    agent_a: str | None
    agent_a_stance: str
    agent_b_stance: str
    agent_b: str | None
    judges: list
    interaction_messages: list
    votes: dict
    winner: str | None
    tournament: bool
    tournament_round: str
    match_number: int
