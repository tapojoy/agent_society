import random

from config import (
    PERSONALITIES,
    SCHOOLS,
    GRADES,
    DOMAINS,
    NEIGHBORHOODS
)


class Agent:

    def __init__(self, name):
        self.name = name

        self.school = random.choice(SCHOOLS)
        self.grade = random.choice(GRADES)
        self.neighborhood = random.choice(NEIGHBORHOODS)
        
        self.personality = random.choice(PERSONALITIES)
        self.confidence = round(random.uniform(0.3, 1.0), 2)
        self.verbosity = round(random.uniform(0.3, 1.0), 2)
        self.persuasiveness = round(random.uniform(0.3, 1.0), 2)
        self.open_mindedness = round(random.uniform(0.3, 1.0), 2)
        self.aggressiveness = round(random.uniform(0.3, 1.0), 2)
        
        # self.debates_participated = 0
        # self.debates_since_last_participation = 0
        self.interactions_participated = 0
        self.interactions_since_last_participation = 0
        self.interaction_history = []
        self.affinity = {}
        
        self.domain_stats = {}
        for domain in DOMAINS:
            self.domain_stats[domain] = {
                "wins": 0,
                "losses": 0,
                "participations": 0
            }

        self.domain_affinity = {}
        for domain in DOMAINS:
            self.domain_affinity[domain] = round(random.uniform(0.2, 0.8), 2)

        self.interests = random.sample(DOMAINS,random.randint(2, 3))
        for interest in self.interests:
            self.domain_affinity[interest] = round(random.uniform(0.8, 1.0), 2)

        self.season_stats = {
            "wins": 0,
            "losses": 0,
            "participations": 0,
            "league_points": 0
        }

