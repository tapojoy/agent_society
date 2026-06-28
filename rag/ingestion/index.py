import json
from pathlib import Path

from connection import (
    get_client,
    close
)

from config import (
    EMBEDDED_DIR,
    COLLECTION_NAME,
    WEAVIATE_ADMIN_API_KEY
)


def index_article(filepath, collection):

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    count = 0

    with collection.batch.dynamic() as batch:

        for chunk in chunks:

            batch.add_object(

                properties={

                    "pageid": chunk["pageid"],
                    "chunk_id": chunk["chunk_id"],
                    "title": chunk["title"],
                    "domain": chunk["domain"],
                    "url": chunk["url"],
                    "revision_id": chunk["revision_id"],
                    "retrieved_at": chunk["retrieved_at"],
                    "source": chunk["source"],
                    "section_title": chunk["section_title"],
                    "section_index": chunk["section_index"],
                    "categories": chunk["categories"],
                    "text": chunk["text"]

                },

                vector=chunk["embedding"]

            )

            count += 1

    if batch.number_errors > 0:

        print(
            f"{batch.number_errors} objects failed "
            f"while indexing {filepath.name}"
        )

    print(
        f"Indexed: {filepath.name} "
        f"({count} chunks)"
    )


def index():

    client = get_client(WEAVIATE_ADMIN_API_KEY)

    collection = client.collections.get(
        COLLECTION_NAME
    )

    files = sorted(
        EMBEDDED_DIR.glob("*.json")
    )

    print(
        f"Indexing {len(files)} articles...\n"
    )

    for filepath in files:

        index_article(
            filepath,
            collection
        )

    print("\nIndexing completed.")


if __name__ == "__main__":

    try:

        index()

    finally:

        close()
