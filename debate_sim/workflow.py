import random

from langgraph.graph import StateGraph, START, END

from state import InteractionState

from config import DOMAINS
from models import create_message
from logger import log_event, log_all_agents
from utils import (
    update_domain_stats,
    update_relationships,
    update_informal_relationship,
    update_domain_affinity_from_interaction
)

from llm.tasks import  (
    generate_topic, 
    generate_opening_statement,
    generate_rebuttal,
    generate_closing_statement,
    judge_debate,
    generate_informal_topic,
    generate_informal_response
)


def log_message(interaction_id, message):
    log_event(
        {
            "event_type": "message",
            "interaction_id": interaction_id,
            **message
        }
    )


##################################################################

def select_topic(state):
    agents = state["participants"]

    if state.get("tournament", False):
        eligible = [
            a for a in agents
            if a.name not in (
                state["pro_agent"],
                state["con_agent"]
            )
        ]
    else:
        eligible = agents

    topic_creator = random.choice(eligible)
    domain = random.choice(DOMAINS)
    topic_response = generate_topic(domain)
    
    state["topic_initiator"] = topic_creator.name
    state["domain"] = domain
    state["topic"] = topic_response["content"]
    
    log_event(
        {
            "event_type": "topic_selected",
            "interaction_id": state["interaction_id"],
            "agent": topic_creator.name,
            "domain": domain,
            **topic_response
        }
    )

    return state


# def assign_roles(state):
#     agents = state["participants"]
#     remaining_agents = [
#         a
#         for a in agents
#         if a.name != state["topic_initiator"]
#     ]

#     pro_agent, con_agent = random.sample(remaining_agents, 2)

#     judges = [
#         a
#         for a in remaining_agents
#         if a.name not in (pro_agent.name, con_agent.name)
#     ]

#     state["pro_agent"] = pro_agent.name
#     state["con_agent"] = con_agent.name
#     state["judges"] = [j.name for j in judges]
#     state["agent_a"] = None
#     state["agent_b"] = None

#     log_event(
#         {
#             "event_type": "roles_assigned",
#             "interaction_id": state["interaction_id"],
#             "pro_agent": pro_agent.name,
#             "con_agent": con_agent.name,
#             "judges": state["judges"]
#         }
#     )

#     return state

def assign_roles(state):
    agents = state["participants"]

    # ---------------------------------------------------------
    # Tournament: preserve the bracket competitors
    # ---------------------------------------------------------
    if state.get("tournament", False):

        pro_agent = next(
            a for a in agents
            if a.name == state["pro_agent"]
        )

        con_agent = next(
            a for a in agents
            if a.name == state["con_agent"]
        )

        topic_creator = next(
            a
            for a in agents
            if a.name == state["topic_initiator"]
        )

        judges = [
            a
            for a in agents
            if a.name not in (
                pro_agent.name,
                con_agent.name,
                topic_creator.name
            )
        ]

        state["judges"] = [j.name for j in judges]
        state["agent_a"] = None
        state["agent_b"] = None

    # ---------------------------------------------------------
    # Regular season: assign roles randomly
    # ---------------------------------------------------------
    else:

        remaining_agents = [
            a
            for a in agents
            if a.name != state["topic_initiator"]
        ]

        pro_agent, con_agent = random.sample(
            remaining_agents,
            2
        )

        judges = [
            a
            for a in remaining_agents
            if a.name not in (
                pro_agent.name,
                con_agent.name
            )
        ]

        state["pro_agent"] = pro_agent.name
        state["con_agent"] = con_agent.name
        state["judges"] = [j.name for j in judges]
        state["agent_a"] = None
        state["agent_b"] = None

    log_event(
        {
            "event_type": "roles_assigned",
            "interaction_id": state["interaction_id"],
            "pro_agent": state["pro_agent"],
            "con_agent": state["con_agent"],
            "judges": state["judges"]
        }
    )

    return state


def opening_round(state):

    agents = state["participants"]
    pro_agent = next(a for a in agents if a.name == state["pro_agent"])
    con_agent = next(a for a in agents if a.name == state["con_agent"])
    domain = state["domain"]

    pro_msg = generate_opening_statement(
            topic=state["topic"],
            side="PRO",
            personality=pro_agent.personality,
            confidence=pro_agent.confidence,
            aggressiveness=pro_agent.aggressiveness,
            persuasiveness=pro_agent.persuasiveness,
            verbosity=pro_agent.verbosity,
            domain=domain,
            interests=pro_agent.interests,
            domain_affinity=pro_agent.domain_affinity[domain]
    )
    con_msg = generate_opening_statement(
            topic=state["topic"],
            side="CON",
            personality=con_agent.personality,
            confidence=con_agent.confidence,
            aggressiveness=con_agent.aggressiveness,
            persuasiveness=con_agent.persuasiveness,
            verbosity=con_agent.verbosity,
            domain=domain,
            interests=con_agent.interests,
            domain_affinity=con_agent.domain_affinity[domain]
    )

    message = create_message(
        interaction_round="opening",
        side="PRO",
        agent=pro_agent,
        message=pro_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)
    
    message = create_message(
        interaction_round="opening",
        side="CON",
        agent=con_agent,
        message=con_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)

    return state


def rebuttal_round_1(state):
    
    agents = state["participants"]
    pro_agent = next(a for a in agents if a.name == state["pro_agent"])
    con_agent = next(a for a in agents if a.name == state["con_agent"])

    last_pro = state["interaction_messages"][0]["message"]
    last_con = state["interaction_messages"][1]["message"]
    domain = state["domain"]

    pro_msg = generate_rebuttal(
            topic=state["topic"],
            side="PRO",
            personality=pro_agent.personality,
            confidence=pro_agent.confidence,
            aggressiveness=pro_agent.aggressiveness,
            persuasiveness=pro_agent.persuasiveness,
            verbosity=pro_agent.verbosity,
            domain=domain,
            interests=pro_agent.interests,
            domain_affinity=pro_agent.domain_affinity[domain],
            opponent_argument=last_con
    )
    con_msg = generate_rebuttal(
            topic=state["topic"],
            side="CON",
            personality=con_agent.personality,
            confidence=con_agent.confidence,
            aggressiveness=con_agent.aggressiveness,
            persuasiveness=con_agent.persuasiveness,
            verbosity=con_agent.verbosity,
            domain=domain,
            interests=con_agent.interests,
            domain_affinity=con_agent.domain_affinity[domain],
            opponent_argument=last_pro
    )

    message = create_message(
        interaction_round="rebuttal_1",
        side="PRO",
        agent=pro_agent,
        message=pro_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)
    
    message = create_message(
        interaction_round="rebuttal_1",
        side="CON",
        agent=con_agent,
        message=con_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)

    return state


def rebuttal_round_2(state):

    agents = state["participants"]
    pro_agent = next(a for a in agents if a.name == state["pro_agent"])
    con_agent = next(a for a in agents if a.name == state["con_agent"])

    last_pro = state["interaction_messages"][-2]["message"]
    last_con = state["interaction_messages"][-1]["message"]
    domain = state["domain"]

    pro_msg = generate_rebuttal(
            topic=state["topic"],
            side="PRO",
            personality=pro_agent.personality,
            confidence=pro_agent.confidence,
            aggressiveness=pro_agent.aggressiveness,
            persuasiveness=pro_agent.persuasiveness,
            verbosity=pro_agent.verbosity,
            domain=domain,
            interests=pro_agent.interests,
            domain_affinity=pro_agent.domain_affinity[domain],
            opponent_argument=last_con
    )
    con_msg = generate_rebuttal(
            topic=state["topic"],
            side="CON",
            personality=con_agent.personality,
            confidence=con_agent.confidence,
            aggressiveness=con_agent.aggressiveness,
            persuasiveness=con_agent.persuasiveness,
            verbosity=con_agent.verbosity,
            domain=domain,
            interests=con_agent.interests,
            domain_affinity=con_agent.domain_affinity[domain],
            opponent_argument=last_pro
    )


    message = create_message(
        interaction_round="rebuttal_2",
        side="PRO",
        agent=pro_agent,
        message=pro_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)
    
    message = create_message(
        interaction_round="rebuttal_2",
        side="CON",
        agent=con_agent,
        message=con_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)

    return state


def closing_round(state):

    agents = state["participants"]
    pro_agent = next(a for a in agents if a.name == state["pro_agent"])
    con_agent = next(a for a in agents if a.name == state["con_agent"])

    history = "\n".join(
        [
            f"{msg['side']}: {msg['message']}"
            for msg in
            state["interaction_messages"]
        ]
    )
    domain = state["domain"]

    pro_msg = generate_closing_statement(
            topic=state["topic"],
            side="PRO",
            personality=pro_agent.personality,
            confidence=pro_agent.confidence,
            aggressiveness=pro_agent.aggressiveness,
            persuasiveness=pro_agent.persuasiveness,
            verbosity=pro_agent.verbosity,
            domain=domain,
            interests=pro_agent.interests,
            domain_affinity=pro_agent.domain_affinity[domain],
            debate_history=history
    )
    con_msg = generate_closing_statement(
            topic=state["topic"],
            side="CON",
            personality=con_agent.personality,
            confidence=con_agent.confidence,
            aggressiveness=con_agent.aggressiveness,
            persuasiveness=con_agent.persuasiveness,
            verbosity=con_agent.verbosity,
            domain=domain,
            interests=con_agent.interests,
            domain_affinity=con_agent.domain_affinity[domain],
            debate_history=history
    )

    message = create_message(
        interaction_round="closing",
        side="PRO",
        agent=pro_agent,
        message=pro_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)
    
    message = create_message(
        interaction_round="closing",
        side="CON",
        agent=con_agent,
        message=con_msg
    )
    state["interaction_messages"].append(message)
    log_message(state["interaction_id"], message)

    return state


def voting(state):
    agents = state["participants"]
    judges = [
        a
        for a in agents
        if a.name in state["judges"]
    ]

    transcript = "\n".join(
        [
            f"{msg['side']}: {msg['message']}"
            for msg in
            state["interaction_messages"]
        ]
    )
    
    domain = state["domain"]
        
    votes = {"PRO": 0, "CON": 0}

    for judge in judges:
        
        judgement = judge_debate(
            state["topic"], 
            transcript,
            personality=judge.personality,
            open_mindedness=judge.open_mindedness,
            domain=domain,
            interests=judge.interests,
            domain_affinity=judge.domain_affinity[domain]
        )
        vote = judgement["content"].strip().upper()
        
        llm_vote_worked=True
        soft_vote=None
        if vote not in ["PRO", "CON"]:
            llm_vote_worked=False
            soft_vote = vote
            vote = random.choice(["PRO", "CON"])
        
        print(f"Vote: {vote}, llm_vote_worked: {llm_vote_worked}")
        
        log_event(
            {
                "event_type": "vote_cast",
                "interaction_id": state["interaction_id"],
                "judge": judge.name,
                "vote": vote,
                "llm_vote_worked": llm_vote_worked,
                "soft_vote": soft_vote
            }
        )
        
        votes[vote] += 1

    state["votes"] = votes

    return state



def winner(state):
    
    agents = state["participants"]
    all_agents = state["all_agents"]
    pro_agent = next(a for a in agents if a.name == state["pro_agent"])
    con_agent = next(a for a in agents if a.name == state["con_agent"])

    if (state["votes"]["PRO"] > state["votes"]["CON"]):
        winner = pro_agent
        loser = con_agent
    else:
        winner = con_agent
        loser = pro_agent
    state["winner"] = winner.name
    domain = state["domain"]

    print("Votes:", state["votes"], "Winner:", state["winner"])

    interaction = {
        "interaction_type": "formal",
        "interaction_id": state["interaction_id"],
        "topic": state["topic"],
        "domain": state["domain"],
        "opponent": loser.name,
        "result": "WIN"
    }
    winner.interaction_history.append(interaction)
    
    interaction = {
        "interaction_type": "formal",
        "interaction_id": state["interaction_id"],
        "topic": state["topic"],
        "domain": state["domain"],
        "opponent": winner.name,
        "result": "LOSS"
    }
    loser.interaction_history.append(interaction)

    update_domain_stats(winner, domain, True)
    update_domain_stats(loser, domain, False)
    update_relationships(winner, loser)

    winner.season_stats["wins"] += 1
    winner.season_stats["participations"] += 1
    if not state.get("tournament", False):
        winner.season_stats["league_points"] += 3
    
    loser.season_stats["losses"] += 1
    loser.season_stats["participations"] += 1
    if not state.get("tournament", False):
        loser.season_stats["league_points"] += 1
    
    log_all_agents(state["interaction_id"], all_agents)
    
    log_event(
        {
            "event_type": "interaction_finished",
            "interaction_type": "formal",
            "interaction_id": state["interaction_id"],
            "winner": state["winner"],
            "topic": state["topic"],
            "votes": state["votes"]
        }
    )

    return state


# ----------------------------------------------------------------
# informal part
# ----------------------------------------------------------------

def assign_informal_roles(state):
    state["topic_initiator"] = None
    state["agent_a"] = state["participants"][0]
    state["agent_b"] = state["participants"][1]

    state["pro_agent"] = None
    state["con_agent"] = None
    state["judges"] = []
    state["votes"] = {}
    state["winner"] = None
    
    return state


def select_informal_topic(state):

    domain = random.choice(DOMAINS)

    response = generate_informal_topic(domain)

    state["domain"] = domain
    state["topic"] = response["content"]
    state["topic_initiator"] = random.choice(
        [state["agent_a"], state["agent_b"]]
    ).name

    log_event(
        {
            "event_type": "informal_topic_selected",
            "interaction_id": state["interaction_id"],
            "domain": domain,
            **response
        }
    )

    return state


def assign_stances(state):

    mode = random.choice(
        [
            ("PRO", "PRO"),
            ("PRO", "CON"),
            ("CON", "CON")
        ]
    )

    state["agent_a_stance"] = mode[0]
    state["agent_b_stance"] = mode[1]

    return state


def informal_round(state):

    agent_a = state["agent_a"]
    agent_b = state["agent_b"]

    domain = state["domain"]

    msg_a = generate_informal_response(
        topic=state["topic"],
        stance=state["agent_a_stance"],
        previous_message=None,
        personality=agent_a.personality,
        confidence=agent_a.confidence,
        aggressiveness=agent_a.aggressiveness,
        persuasiveness=agent_a.persuasiveness,
        verbosity=agent_a.verbosity,
        domain=domain,
        interests=agent_a.interests,
        domain_affinity=agent_a.domain_affinity[domain]
    )

    message = create_message(
        interaction_round="discussion",
        side=state["agent_a_stance"],
        agent=agent_a,
        message=msg_a
    )

    state["interaction_messages"].append(message)

    log_message(
        state["interaction_id"],
        message
    )

    msg_b = generate_informal_response(
        topic=state["topic"],
        stance=state["agent_b_stance"],
        previous_message=msg_a["content"],
        personality=agent_b.personality,
        confidence=agent_b.confidence,
        aggressiveness=agent_b.aggressiveness,
        persuasiveness=agent_b.persuasiveness,
        verbosity=agent_b.verbosity,
        domain=domain,
        interests=agent_b.interests,
        domain_affinity=agent_b.domain_affinity[domain]
    )

    message = create_message(
        interaction_round="discussion",
        side=state["agent_b_stance"],
        agent=agent_b,
        message=msg_b
    )

    state["interaction_messages"].append(message)

    log_message(
        state["interaction_id"],
        message
    )

    return state


def update_informal_state(state):

    agent_a = state["agent_a"]
    agent_b = state["agent_b"]

    stance_a = state["agent_a_stance"]
    stance_b = state["agent_b_stance"]

    domain = state["domain"]

    outcome = update_informal_relationship(
        agent_a,
        agent_b,
        stance_a,
        stance_b
    )

    positive = outcome in (
        "agreement",
        "respectful_disagreement"
    )

    update_domain_affinity_from_interaction(
        agent_a,
        domain,
        positive
    )

    update_domain_affinity_from_interaction(
        agent_b,
        domain,
        positive
    )

    interaction = {
        "interaction_type": "informal",
        "interaction_id": state["interaction_id"],
        "domain": domain,
        "topic": state["topic"],
        "other_agent": agent_b.name,
        "stance": stance_a,
        "interaction_mode": (
            f"{stance_a}_{stance_b}"
        ),
        "outcome": outcome
    }

    agent_a.interaction_history.append(interaction)

    interaction = {
        "interaction_type": "informal",
        "interaction_id": state["interaction_id"],
        "domain": domain,
        "topic": state["topic"],
        "other_agent": agent_a.name,
        "stance": stance_b,
        "interaction_mode": (
            f"{stance_a}_{stance_b}"
        ),
        "outcome": outcome
    }

    agent_b.interaction_history.append(interaction)

    log_all_agents(
        state["interaction_id"],
        state["all_agents"]
    )

    log_event(
        {
            "event_type": "interaction_finished",
            "interaction_type": "informal",
            "interaction_id": state["interaction_id"],
            "topic": state["topic"],
            "domain": domain,
            "interaction_mode": (
                f"{stance_a}_{stance_b}"
            ),
            "outcome": outcome
        }
    )

    return state


##################################################################

def interaction_router(state):
    return state["interaction_type"]


builder = StateGraph(InteractionState)

builder.add_node("assign_informal_roles", assign_informal_roles)
builder.add_node("select_informal_topic", select_informal_topic)
builder.add_node("assign_stances", assign_stances)
builder.add_node("informal_round", informal_round)
builder.add_node("update_informal_state", update_informal_state)

builder.add_node("select_topic", select_topic)
builder.add_node("assign_roles", assign_roles)
builder.add_node("opening_round", opening_round)
builder.add_node("rebuttal_round_1", rebuttal_round_1)
builder.add_node("rebuttal_round_2", rebuttal_round_2)
builder.add_node("closing_round", closing_round)
builder.add_node("voting", voting)
builder.add_node("winner", winner)


builder.add_conditional_edges(
    START,
    interaction_router,
    {
        "formal": "select_topic",
        "informal": "assign_informal_roles"
    }
)

builder.add_edge("assign_informal_roles", "select_informal_topic")
builder.add_edge("select_informal_topic", "assign_stances")
builder.add_edge("assign_stances", "informal_round")
builder.add_edge("informal_round", "update_informal_state")
builder.add_edge("update_informal_state", END)

builder.add_edge("select_topic", "assign_roles")
builder.add_edge("assign_roles", "opening_round")
builder.add_edge("opening_round", "rebuttal_round_1")
builder.add_edge("rebuttal_round_1", "rebuttal_round_2")
builder.add_edge("rebuttal_round_2", "closing_round")
builder.add_edge("closing_round", "voting")
builder.add_edge("voting", "winner")
builder.add_edge("winner", END)

graph = builder.compile()

