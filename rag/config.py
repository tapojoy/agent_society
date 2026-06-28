from pathlib import Path

from dotenv import load_dotenv

import os


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

INGESTION_DIR = BASE_DIR / "ingestion"

RAW_ARTICLES_DIR = INGESTION_DIR / "raw_articles"
PROCESSED_ARTICLES_DIR = INGESTION_DIR / "processed_articles"
CHUNK_DIR = INGESTION_DIR / "chunks"
EMBEDDED_DIR = INGESTION_DIR / "embedded"

RAW_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
CHUNK_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDED_DIR.mkdir(parents=True, exist_ok=True)

MEDIAWIKI_API = os.getenv("MEDIAWIKI_API")
USER_AGENT = os.getenv("USER_AGENT")

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_RAG_USER = os.getenv("WEAVIATE_RAG_USER")
WEAVIATE_RAG_API_KEY = os.getenv("WEAVIATE_RAG_API_KEY")
WEAVIATE_ADMIN_USER = os.getenv("WEAVIATE_ADMIN_USER")
WEAVIATE_ADMIN_API_KEY = os.getenv("WEAVIATE_ADMIN_API_KEY")

WEAVIATE_HTTP_PORT = int(os.getenv("WEAVIATE_HTTP_PORT", 8080))
WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

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

