def create_message(
    interaction_round,
    side,
    agent,
    message
):

    return {
        "round": interaction_round,
        "side": side,
        "speaker": agent.name,
        "personality": agent.personality,
        "confidence": agent.confidence,
        "aggressiveness": agent.aggressiveness,
        "persuasiveness": agent.persuasiveness,
        "verbosity": agent.verbosity,
        "school": agent.school,
        "grade": agent.grade,
        "neighborhood": agent.neighborhood,
        "interests": agent.interests,
        "request_id": message["request_id"],
        "message": message["content"],
        "model": message["model"],
        "client_latency_ms": message["client_latency_ms"],
        "server_latency_ms": message["server_latency_ms"],
        "prompt_tokens": message["prompt_tokens"],
        "completion_tokens": message["completion_tokens"],
        
    }
