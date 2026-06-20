import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL")
API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL_1 = os.getenv("OLLAMA_MODEL_1")
MODEL_2 = os.getenv("OLLAMA_MODEL_2")
MODEL_3 = os.getenv("OLLAMA_MODEL_3")

AGENT_COUNT = 32
NUM_PARTICIPANTS = 8
TOTAL_INTERACTIONS = 32 #128

PERSONALITIES = [
    "Analytical",
    "Emotional",
    "Pragmatic",
    "Idealistic",
    "Skeptical"
]

SCHOOLS = [
    "North Valley High",
    "Central Public School",
    "Greenfield Academy",
    "Riverside School",
    "Horizon High"
]

GRADES = [
    9,
    10,
    11,
    12
]

DOMAINS = [
    "Technology",
    "Science",
    "History",
    "Politics",
    "Environment",
    "Engineering",
    "Economics"
]

NEIGHBORHOODS = [
    "North District",
    "South District",
    "East District",
    "West District",
    "Central District"
]

INITIALIZATION_MODE = "fresh" # fresh OR resume
POPULATION_FILE = "population.json"
