import random
import uuid
import json
import traceback

from logger import (
    log_event,
    log_operation,
    log_all_agents
)

from agents import Agent


# ------------------------------------------------------------------

def run_tournament(
    graph,
    all_agents,
    session_id,
    interaction_start_no
):
    """
    Top-8 knockout tournament.

    Returns the champion Agent.
    """

    standings = sorted(
        all_agents,
        key=lambda agent: (
            agent.season_stats["league_points"],
            agent.season_stats["wins"],
            agent.confidence
        ),
        reverse=True
    )

    qualified = standings[:8]

    log_operation(
        "tournament_started",
        "INFO",
        {
            "qualified": [a.name for a in qualified]
        }
    )

    print("\n=== TOURNAMENT QUALIFIERS ===")

    for seed, agent in enumerate(qualified, start=1):

        print(
            f"{seed}. "
            f"{agent.name} "
            f"({agent.season_stats['league_points']} pts)"
        )

    rounds = [
        "quarter_final",
        "semi_final",
        "final"
    ]

    current = qualified

    interaction_no = interaction_start_no

    for stage in rounds:

        winners = []

        print(f"\n=== {stage.upper()} ===")

        for match_no in range(0, len(current), 2):

            pro = current[match_no]
            con = current[match_no + 1]

            try:

                remaining = [
                    a
                    for a in all_agents
                    if a.name not in (
                        pro.name,
                        con.name
                    )
                ]

                judges = random.sample(
                    remaining,
                    6
                )

                participants = [
                    pro,
                    con,
                    *judges
                ]

                interaction_id = (
                    f"{session_id[:8]}_T{interaction_no}"
                )

                state = {

                    "status": "RUNNING",

                    "session_id": session_id,

                    "interaction_no": interaction_no,
                    "interaction_id": interaction_id,
                    "interaction_type": "formal",

                    "participants": participants,
                    "all_agents": all_agents,

                    "domain": "",
                    "topic": "",
                    "topic_initiator": "",

                    "pro_agent": pro.name,
                    "con_agent": con.name,
                    "judges": [],

                    "agent_a": None,
                    "agent_b": None,
                    "agent_a_stance": "",
                    "agent_b_stance": "",

                    "interaction_messages": [],

                    "votes": {},

                    "winner": "",

                    "tournament": True,
                    "stage": stage,
                    "match_number": (
                        match_no // 2
                    ) + 1
                }

                log_operation(
                    "tournament_match_started",
                    "INFO",
                    {
                        "interaction_id": interaction_id,
                        "stage": stage,
                        "pro": pro.name,
                        "con": con.name,
                        "judges": [
                            j.name
                            for j in judges
                        ]
                    }
                )

                result = graph.invoke(
                    state
                )

                winner_name = (
                    result["winner"]
                )

                winner = next(
                    a
                    for a in all_agents
                    if a.name == winner_name
                )

                winners.append(
                    winner
                )

                log_event(
                    {
                        "event_type": (
                            "tournament_match_finished"
                        ),
                        "interaction_id": (
                            interaction_id
                        ),
                        "stage": stage,
                        "winner": winner.name,
                        "votes": result["votes"]
                    }
                )

                log_all_agents(
                    interaction_id,
                    all_agents
                )

                interaction_no += 1

            except Exception as e:

                log_operation(
                    "tournament_match_failed",
                    "ERROR",
                    {
                        "stage": stage,
                        "pro": pro.name,
                        "con": con.name,
                        "error": str(e),
                        "traceback": (
                            traceback.format_exc()
                        )
                    }
                )

                raise

        current = winners

    champion = current[0]

    log_event(
        {
            "event_type": (
                "tournament_finished"
            ),
            "champion": champion.name
        }
    )

    log_operation(
        "tournament_completed",
        "INFO",
        {
            "champion": champion.name
        }
    )

    print("\n=== LEAGUE CHAMPION ===")
    print(champion.name)

    return champion


# ------------------------------------------------------------------


def save_population(agents, filepath):
    """
    Save the current agent population so that a future
    simulation can resume from this state.
    """
    population = []
    for agent in agents:
        population.append({
            "name": agent.name,
            "school": agent.school,
            "grade": agent.grade,
            "neighborhood": agent.neighborhood,
            "personality": agent.personality,
            "confidence": agent.confidence,
            "verbosity": agent.verbosity,
            "persuasiveness": agent.persuasiveness,
            "open_mindedness": agent.open_mindedness,
            "aggressiveness": agent.aggressiveness,
            "interactions_participated": agent.interactions_participated,
            "interactions_since_last_participation": agent.interactions_since_last_participation,
            "affinity": agent.affinity,
            "domain_stats": agent.domain_stats,
            "domain_affinity": agent.domain_affinity,
            "interests": agent.interests,
            "season_stats": agent.season_stats,
            "interaction_history": agent.interaction_history

        })
    with open(filepath, "w") as f:
        json.dump(population, f, indent=4)


def load_population(filepath):
    """
    Restore a previously saved population.
    """

    with open(filepath, "r") as f:
        population = json.load(f)

    agents = []
    for record in population:
        agent = Agent(record["name"])
        agent.school = record["school"]
        agent.grade = record["grade"]
        agent.neighborhood = record["neighborhood"]
        agent.personality = record["personality"]
        agent.confidence = record["confidence"]
        agent.verbosity = record["verbosity"]
        agent.persuasiveness = record["persuasiveness"]
        agent.open_mindedness = record["open_mindedness"]
        agent.aggressiveness = record["aggressiveness"]
        agent.interactions_participated = record["interactions_participated"]
        agent.interactions_since_last_participation = record["interactions_since_last_participation"]
        agent.affinity = record["affinity"]
        agent.interests = record["interests"]
        agent.domain_stats = record["domain_stats"]
        agent.domain_affinity = record["domain_affinity"]
        agent.season_stats = record["season_stats"]
        agent.interaction_history = record["interaction_history"]
        agents.append(agent)
    return agents


def select_participants(agents, num_participants, interaction_type):
    for agent in agents:
        agent.interactions_since_last_participation += 1
    eligible = [
        agent
        for agent in agents
        if agent.interactions_since_last_participation >= 3
    ]
    if len(eligible) < num_participants:
        eligible = agents
    if interaction_type == "formal":
        participants = random.sample(eligible, num_participants)
    else:
        agent_a = random.choice(eligible)
        candidates = []
        weights = []
        for agent_b in eligible:
            if agent_b.name == agent_a.name:
                continue
            weight = 5 # everyone has a small chance
            if agent_b.school == agent_a.school:
                weight += 60
            if agent_b.grade == agent_a.grade:
                weight += 25
            if agent_b.neighborhood == agent_a.neighborhood:
                weight += 10
            candidates.append(agent_b)
            weights.append(weight)
        agent_b = random.choices(candidates, weights=weights, k=1)[0]
        participants = [agent_a, agent_b]
    for agent in participants:
        agent.interactions_since_last_participation = 0
        agent.interactions_participated += 1
        agent.season_stats["participations"] += 1
    return participants


def update_domain_stats(agent, domain, won):
    stats = agent.domain_stats[domain]
    stats["participations"] += 1
    if won: stats["wins"] += 1
    else: stats["losses"] += 1
    
    current = agent.domain_affinity[domain]
    if won: current += 0.03
    else: current -= 0.01
    current = max(0.0, min(1.0, current))
    agent.domain_affinity[domain] = round(current, 2)


def create_affinity_if_missing(agent_a, agent_b):
    if agent_b.name not in agent_a.affinity:
        agent_a.affinity[agent_b.name] = 0.0


def update_affinity(agent_a, agent_b, delta):
    create_affinity_if_missing(agent_a, agent_b)
    value = agent_a.affinity[agent_b.name]
    value += delta
    value = max(-1.0, min(1.0, value))
    agent_a.affinity[agent_b.name] = round(value, 2)


def update_relationships(winner, loser):
    winner.confidence = min(1.0, winner.confidence + 0.01)
    loser.confidence = max(0.0, loser.confidence - 0.01)
    winner.season_stats["wins"] += 1
    winner.season_stats["league_points"] += 3
    loser.season_stats["losses"] += 1
    update_affinity(winner, loser, -0.05)
    update_affinity(loser, winner, -0.05)


# ------------------------------------------------------------------


def update_informal_relationship(agent_a, agent_b, stance_a, stance_b):
    """
    Update affinity and confidence after an informal interaction.
    """

    create_affinity_if_missing(agent_a, agent_b)
    create_affinity_if_missing(agent_b, agent_a)

    if stance_a == stance_b:
        # Agreement strengthens relationship
        delta = 0.03
        outcome = "agreement"

    else:
        # Disagreement depends on personalities
        tolerance = (
            (agent_a.open_mindedness + agent_b.open_mindedness)
            - (agent_a.aggressiveness + agent_b.aggressiveness)
        ) / 2

        if tolerance >= 0:
            delta = 0.01
            outcome = "respectful_disagreement"
        else:
            delta = -0.03
            outcome = "disagreement"

    update_affinity(agent_a, agent_b, delta)
    update_affinity(agent_b, agent_a, delta)

    confidence_delta = delta / 5

    agent_a.confidence = round(
        max(0.0, min(1.0, agent_a.confidence + confidence_delta)),
        2
    )

    agent_b.confidence = round(
        max(0.0, min(1.0, agent_b.confidence + confidence_delta)),
        2
    )

    return outcome


def update_domain_affinity_from_interaction(agent, domain, positive):
    """
    Informal interactions slowly influence interests.
    """
    delta = 0.01 if positive else -0.005

    value = agent.domain_affinity[domain]
    value += delta
    value = max(0.0, min(1.0, value))

    agent.domain_affinity[domain] = round(value, 2)


# def run_tournament(graph, all_agents, session_id):
#     """
#     Top-8 knockout tournament.

#     Returns the champion Agent.
#     """

#     standings = sorted(
#         all_agents,
#         key=lambda agent: (
#             agent.season_stats["league_points"],
#             agent.season_stats["wins"],
#             agent.confidence
#         ),
#         reverse=True
#     )

#     qualified = standings[:8]

#     print("\n=== TOURNAMENT QUALIFIERS ===")

#     for seed, agent in enumerate(qualified, start=1):
#         print(
#             f"{seed}. {agent.name} "
#             f"({agent.season_stats['league_points']} pts)"
#         )

#     rounds = [
#         "quarter_final",
#         "semi_final",
#         "final"
#     ]

#     current = qualified

#     for round_name in rounds:

#         print(f"\n=== {round_name.upper()} ===")

#         winners = []

#         for match_no in range(0, len(current), 2):

#             pro = current[match_no]
#             con = current[match_no + 1]

#             judge_pool = [
#                 a
#                 for a in all_agents
#                 if a.name not in (pro.name, con.name)
#             ]

#             judges = random.sample(judge_pool, 6)

#             participants = [
#                 pro,
#                 con,
#                 *judges
#             ]

#             interaction_id = (
#                 f"{session_id[:8]}_"
#                 f"{round_name}_"
#                 f"{match_no//2 + 1}_"
#                 f"{uuid.uuid4().hex[:6]}"
#             )

#             state = {
#                 "status": "RUNNING",

#                 "session_id": session_id,

#                 "interaction_no": -1,
#                 "interaction_id": interaction_id,
#                 "interaction_type": "formal",

#                 "participants": participants,
#                 "all_agents": all_agents,

#                 "domain": "",
#                 "topic": "",
#                 "topic_initiator": "",

#                 "pro_agent": "",
#                 "con_agent": "",

#                 "agent_a": None,
#                 "agent_b": None,

#                 "agent_a_stance": "",
#                 "agent_b_stance": "",

#                 "judges": [],
#                 "interaction_messages": [],

#                 "votes": {},
#                 "winner": "",

#                 "tournament": True,
#                 "tournament_round": round_name,
#                 "match_number": match_no // 2 + 1
#             }

#             result = graph.invoke(state)

#             winner_name = result["winner"]

#             winner = next(
#                 a
#                 for a in participants
#                 if a.name == winner_name
#             )

#             winners.append(winner)

#             loser = (
#                 con
#                 if winner.name == pro.name
#                 else pro
#             )

#             print(
#                 f"{pro.name} vs "
#                 f"{con.name} "
#                 f"-> {winner.name}"
#             )

#         current = winners

#     champion = current[0]

#     print("\n=== LEAGUE CHAMPION ===")
#     print(champion.name)

#     return champion

