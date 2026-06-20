import json
import uuid
from datetime import datetime


def log_event(event):
    event["timestamp"] = datetime.utcnow().isoformat()
    event["event_id"] = str(uuid.uuid4())
    with open("logs/events.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")


def log_operation(event_type, level, details=None):
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "level": level,
        "details": details or {}
    }
    with open("logs/operations.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")


def log_agent_state(interaction_id, agent):
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "snapshot_type": "post_interaction",
        "interaction_id": interaction_id,
        "agent": agent.name,
        "school": agent.school,
        "grade": agent.grade,
        "neighborhood": agent.neighborhood,
        "personality": agent.personality,
        "confidence": agent.confidence,
        "persuasiveness": agent.persuasiveness,
        "aggressiveness": agent.aggressiveness,
        "verbosity": agent.verbosity,
        "open_mindedness": agent.open_mindedness,
        "interactions_participated": agent.interactions_participated,
        "interactions_since_last_participation": agent.interactions_since_last_participation,
        "season_stats": agent.season_stats,
        "domain_stats": agent.domain_stats,
        "domain_affinity": agent.domain_affinity,
        "affinity_count": len(agent.affinity),
        "interaction_count": len(agent.interaction_history)
    }
    with open("logs/agent_state.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")


def log_all_agents(interaction_id, agents):
    for agent in agents:
        log_agent_state(interaction_id, agent)
