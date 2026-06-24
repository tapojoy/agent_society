from pathlib import Path

from dotenv import load_dotenv

import os


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

RAW_ARTICLES_DIR = BASE_DIR / "raw_articles"
PROCESSED_ARTICLES_DIR = BASE_DIR / "processed_articles"

RAW_ARTICLES_DIR.mkdir(exist_ok=True)
PROCESSED_ARTICLES_DIR.mkdir(exist_ok=True)

MEDIAWIKI_API = os.getenv("MEDIAWIKI_API")
USER_AGENT = os.getenv("USER_AGENT")

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

DOMAINS = [
    "Technology",
    "Science",
    "History",
    "Politics",
    "Environment",
    "Engineering",
    "Economics"
]

MAX_ARTICLES_PER_DOMAIN = 100

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

TOP_K = 5

