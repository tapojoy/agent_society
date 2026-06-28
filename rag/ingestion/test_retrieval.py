import requests

from connection import (
    get_client,
    close
)

from config import (
    COLLECTION_NAME,
    WEAVIATE_RAG_API_KEY,
    OLLAMA_HOST,
    OLLAMA_API_KEY,
    EMBEDDING_MODEL,
    TOP_K
)


KEYWORDS = [
    "Photosynthesis",      # Science
    "Robotics",            # Engineering
    "Supply and Demand",   # Economics
    "Greenhouse Effect",   # Environment
    "Electric Vehicle"     # Technology
]


def generate_embedding(text):

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

    data = response.json()

    return data["embedding"]


def retrieve(client, query, top_k=TOP_K):

    embedding = generate_embedding(query)

    collection = client.collections.get(
        COLLECTION_NAME
    )

    response = collection.query.near_vector(
        near_vector=embedding,
        limit=top_k,
        return_metadata=["distance"]
    )

    return response.objects


def main():

    client = get_client(
        WEAVIATE_RAG_API_KEY
    )

    try:

        for query in KEYWORDS:

            print("\n" + "=" * 100)

            print("\nQuery:")
            print("-" * 80)
            print(query)
            print("-" * 80)

            results = retrieve(
                client,
                query
            )

            print(f"\nTop {len(results)} Results\n")

            for i, obj in enumerate(results, start=1):

                print("=" * 80)
                print(f"Rank: {i}")

                print(f"Distance : {obj.metadata.distance:.4f}")
                print(f"Title    : {obj.properties['title']}")
                print(f"Section  : {obj.properties['section_title']}")
                print(f"Domain   : {obj.properties['domain']}")
                print(f"URL      : {obj.properties['url']}")

                print("\nChunk:\n")
                print(obj.properties["text"][:800])
                print()

    finally:

        close()


if __name__ == "__main__":
    main()
