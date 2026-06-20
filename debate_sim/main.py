from workflow import graph
import uuid
import traceback

from agents import Agent
from logger import log_operation
from utils import (
    select_participants,
    save_population,
    load_population,
    run_tournament
)

from config import (
    INITIALIZATION_MODE,
    POPULATION_FILE,
    NUM_PARTICIPANTS,
    AGENT_COUNT,
    TOTAL_INTERACTIONS
)
import random

SESSION_ID = str(uuid.uuid4())

if INITIALIZATION_MODE == "resume":
    all_agents = load_population(POPULATION_FILE)
else:
    all_agents = [Agent(f"Agent{i}") for i in range(1, AGENT_COUNT + 1)]

for i in range(0, TOTAL_INTERACTIONS):

    interaction_id = f"{SESSION_ID[:8]}_{i+1}"

    if i % 4 == 0:
        interaction_type = "formal"
        participants = select_participants(all_agents, NUM_PARTICIPANTS)
    else:
        interaction_type = "informal"
        participants = select_participants(all_agents, 2)

    print(f"{interaction_type.upper()} : {interaction_id}")
    print([a.name for a in participants])

    state = {
        "status": "RUNNING",
        "session_id": SESSION_ID,

        "interaction_no": i+1,
        "interaction_id": interaction_id,
        "interaction_type": interaction_type,

        "participants": participants,
        "all_agents": all_agents,

        "domain": "",
        "topic": "",
        "topic_initiator": "",

        # Formal interaction
        "pro_agent": "",
        "con_agent": "",
        "judges": [],
        "votes": {},
        "winner": "",

        # Informal interaction
        "agent_a": "",
        "agent_b": "",

        "tournament": False,
        
        "interaction_messages": []
    }
    
    try:
        state["status"] = "STARTED"
        log_operation(
            "interaction_started",
            "INFO",
            {
                "interaction_id": interaction_id,
                "interaction_type": interaction_type
            }
        )
        
        graph.invoke(state)
        # if interaction_type = "formal":
        #     for msg in state["interaction_messages"]:
        #         print(
        #             f"[{msg['round']}] "
        #             f"{msg['speaker']} "
        #             f"({msg['side']}): "
        #             f"{msg['message']}\n\n\n"
        #         )
    
    except Exception as e:
        print()
        print()
        print(traceback.format_exc())
        state["status"] = "FAILED"
        log_operation(
            "interaction_failed",
            "ERROR",
            {
                "interaction_id": interaction_id,
                "interaction_type": interaction_type,
                "error": str(e),
                "exception_name": type(e).__name__,
                "exception_module": type(e).__module__,
                "traceback": traceback.format_exc()
            }
        )
        continue
    
    state["status"] = "COMPLETED"
    log_operation(
        "interaction_completed",
        "INFO",
        {
            "interaction_id": interaction_id,
            "interaction_type": interaction_type
        }
    )


champion = run_tournament(
    graph=graph,
    all_agents=all_agents,
    session_id=SESSION_ID,
    interaction_start_no=TOTAL_INTERACTIONS + 1
)

save_population(all_agents, POPULATION_FILE)
log_operation(
    "season_completed",
    "INFO",
    {
        "session_id": SESSION_ID,
        "interactions": TOTAL_INTERACTIONS,
        "population_file": POPULATION_FILE
    }
)

