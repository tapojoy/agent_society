import json
import time
from pathlib import Path

import requests

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential
)

from config import (
    OLLAMA_HOST,
    OLLAMA_API_KEY,
    EMBEDDING_MODEL,
    PROCESSED_ARTICLES_DIR
)


CHUNK_DIR = (
    PROCESSED_ARTICLES_DIR.parent /
    "chunks"
)

EMBEDDED_DIR = (
    PROCESSED_ARTICLES_DIR.parent /
    "embedded"
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=20)
)
def generate_embedding(text):

    start = time.perf_counter()

    response = requests.post(
        f"{OLLAMA_HOST}/embed",
        headers={
            "X-API-Key": OLLAMA_API_KEY
        },
        json={
            "model": EMBEDDING_MODEL,
            "text": text
        },
        timeout=(5, 300)
    )

    response.raise_for_status()

    latency = (
        time.perf_counter() - start
    )

    data = response.json()

    return (
        data["embedding"],
        latency,
        data["request_id"]
    )


def embed_article(filepath, article_no, total_articles):

    output = (
        EMBEDDED_DIR /
        filepath.name
    )

    if output.exists():

        print(
            f"[Article {article_no}/{total_articles}] "
            f"Skipping: {filepath.name}"
        )

        return

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    embedded_chunks = []

    total_chunks = len(chunks)

    article_start = time.perf_counter()

    for chunk_no, chunk in enumerate(chunks, start=1):

        embedding, latency, request_id = (generate_embedding(chunk["text"]))

        chunk["embedding"] = embedding
        chunk["request_id"] = request_id

        embedded_chunks.append(
            chunk
        )

        print(
            f"[Article {article_no}/{total_articles}] "
            f"{filepath.stem} | "
            f"Chunk {chunk_no}/{total_chunks} | "
            f"{latency:.2f}s"
        )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            embedded_chunks,
            f,
            ensure_ascii=False
        )

    article_elapsed = (
        time.perf_counter() - article_start
    )

    print(
        f"Embedded: {filepath.name} "
        f"({total_chunks} chunks, "
        f"{article_elapsed:.2f}s)"
    )


def embed():

    Path(
        EMBEDDED_DIR
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    files = sorted(
        CHUNK_DIR.glob("*.json")
    )

    total_articles = len(files)

    print(
        f"Embedding {total_articles} articles...\n"
    )

    for article_no, filepath in enumerate(files, start=1):

        embed_article(
            filepath,
            article_no,
            total_articles
        )


if __name__ == "__main__":
    embed()