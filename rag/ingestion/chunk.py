import json
from pathlib import Path

from config import (
    PROCESSED_ARTICLES_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


CHUNK_DIR = (
    PROCESSED_ARTICLES_DIR.parent /
    "chunks"
)


def split_long_paragraph(paragraph):
    """
    Split a paragraph only if it exceeds CHUNK_SIZE.
    """

    words = paragraph.split()

    if len(words) <= CHUNK_SIZE:
        return [paragraph]

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + CHUNK_SIZE,
            len(words)
        )

        chunks.append(
            " ".join(words[start:end])
        )

        if end == len(words):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def chunk_section(section):

    paragraphs = [
        p.strip()
        for p in section["text"].split("\n\n")
        if p.strip()
    ]

    chunks = []

    current = []

    current_words = 0

    for paragraph in paragraphs:

        words = len(
            paragraph.split()
        )

        #
        # Very large paragraph.
        #
        if words > CHUNK_SIZE:

            if current:

                chunks.append(
                    "\n\n".join(current)
                )

                current = []
                current_words = 0

            chunks.extend(
                split_long_paragraph(
                    paragraph
                )
            )

            continue

        #
        # Fits current chunk.
        #
        if (
            current_words + words
            <= CHUNK_SIZE
        ):

            current.append(
                paragraph
            )

            current_words += words

        #
        # Start new chunk.
        #
        else:

            chunks.append(
                "\n\n".join(current)
            )

            current = [
                paragraph
            ]

            current_words = words

    if current:

        chunks.append(
            "\n\n".join(current)
        )

    return chunks


def chunk_article(filepath):

    output = (
        CHUNK_DIR /
        filepath.name
    )

    if output.exists():

        print(
            f"Skipping chunked: {filepath.name}"
        )

        return

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        article = json.load(f)

    chunk_objects = []

    chunk_id = 0

    for section_index, section in enumerate(
        article["sections"]
    ):

        section_chunks = chunk_section(
            section
        )

        for text in section_chunks:

            chunk_objects.append(
                {
                    "chunk_id": chunk_id,
                    "pageid": article["pageid"],
                    "title": article["title"],
                    "domain": article["domain"],
                    "url": article["url"],
                    "revision_id": article["revision_id"],
                    "retrieved_at": article["retrieved_at"],
                    "source": article["source"],
                    "categories": article["categories"],
                    "section_title": section["title"],
                    "section_index": section_index,
                    "text": text
                }
            )

            chunk_id += 1

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunk_objects,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"Chunked: "
        f"{article['title']} "
        f"({len(chunk_objects)} chunks)"
    )


def chunk():

    Path(
        CHUNK_DIR
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    for filepath in sorted(
        PROCESSED_ARTICLES_DIR.glob("*.json")
    ):

        chunk_article(
            filepath
        )


if __name__ == "__main__":
    chunk()