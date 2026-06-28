import requests

from connection import (
    get_client,
    close
)

from config import (
    OLLAMA_HOST,
    OLLAMA_API_KEY,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    WEAVIATE_ADMIN_API_KEY
)


TEST_TEXT = (
    "Artificial intelligence is transforming society."
)


def test_ollama():

    print("=== Testing Ollama ===")

    response = requests.post(
        f"{OLLAMA_HOST}/embed",
        headers={
            "X-API-Key": OLLAMA_API_KEY
        },
        json={
            "model": EMBEDDING_MODEL,
            "text": TEST_TEXT
        },
        timeout=(5, 60)
    )

    response.raise_for_status()

    data = response.json()

    embedding = data["embedding"]

    print(f"Model: {EMBEDDING_MODEL}")
    print(f"Embedding dimensions: {len(embedding)}")
    print("Ollama connection: OK")


def test_weaviate():

    print("\n=== Testing Weaviate ===")

    client = get_client(WEAVIATE_ADMIN_API_KEY)

    print("Connection: OK")

    exists = client.collections.exists(
        COLLECTION_NAME
    )

    print(
        f"Collection '{COLLECTION_NAME}': "
        f"{'FOUND' if exists else 'NOT FOUND'}"
    )


def main():

    try:

        test_ollama()

        test_weaviate()

        print("\nAll connection tests passed.")

    finally:

        close()


if __name__ == "__main__":
    main()
