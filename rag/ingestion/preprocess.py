import json
import re
from pathlib import Path

from config import (
    RAW_ARTICLES_DIR,
    PROCESSED_ARTICLES_DIR
)

MIN_ARTICLE_LENGTH = 500

SKIP_SECTIONS = {
    "See also",
    "References",
    "Further reading",
    "External links",
    "Bibliography",
    "Notes"
}


def normalize_whitespace(text):
    """
    Normalize whitespace while preserving paragraph breaks.
    """
    paragraphs = []

    for paragraph in text.split("\n\n"):

        paragraph = re.sub(
            r"[ \t]+",
            " ",
            paragraph
        ).strip()

        if paragraph:
            paragraphs.append(paragraph)

    return "\n\n".join(paragraphs)


def remove_empty_lines(text):
    """
    Collapse multiple blank lines into a single blank line.
    """
    text = text.replace("\r\n", "\n")

    text = re.sub(
        r"\n[ \t]*\n+",
        "\n\n",
        text
    )

    return text.strip()


def remove_citation_artifacts(text):

    text = re.sub(
        r"\[\d+\]",
        "",
        text
    )

    text = re.sub(
        r"\[citation needed\]",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\[clarification needed\]",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text


def split_into_sections(text):

    sections = []

    current_title = "Introduction"
    current_lines = []

    for line in text.splitlines():

        if re.fullmatch(
            r"\s*=+\s*.+?\s*=+\s*",
            line
        ):

            if current_lines:

                section_text = normalize_whitespace(
                    "\n".join(current_lines)
                )

                if (
                    current_title not in SKIP_SECTIONS
                    and section_text
                ):
                    sections.append(
                        {
                            "title": current_title,
                            "text": section_text
                        }
                    )

            current_title = (
                line.strip()
                .strip("=")
                .strip()
            )

            current_lines = []

        else:

            current_lines.append(line)

    if current_lines:

        section_text = normalize_whitespace(
            "\n".join(current_lines)
        )

        if (
            current_title not in SKIP_SECTIONS
            and section_text
        ):
            sections.append(
                {
                    "title": current_title,
                    "text": section_text
                }
            )

    return sections


def is_valid_article(page):

    title = page.get(
        "title",
        ""
    ).lower()

    if (
        "(disambiguation)" in title
        or title.startswith("list of")
        or title.startswith("portal:")
        or title.startswith("template:")
        or title.startswith("category:")
        or title.startswith("help:")
        or title.startswith("draft:")
        or title.startswith("file:")
    ):
        return False

    if page.get("redirect", False):
        return False

    text = page.get(
        "extract",
        ""
    )

    if len(text.strip()) < MIN_ARTICLE_LENGTH:
        return False

    if "this article is a stub" in text.lower():
        return False

    return True


def preprocess_article(filepath):

    output = (
        PROCESSED_ARTICLES_DIR /
        filepath.name
    )

    if output.exists():

        print(
            f"Skipping processed: {filepath.name}"
        )

        return

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        raw = json.load(f)

    page = next(
        iter(
            raw["response"]["query"]["pages"].values()
        )
    )

    if not is_valid_article(page):

        print(
            f"Filtered: {page.get('title')}"
        )

        return

    text = page.get(
        "extract",
        ""
    )

    text = remove_citation_artifacts(text)
    text = remove_empty_lines(text)

    sections = split_into_sections(text)

    processed = {
        "pageid": page["pageid"],
        "title": page["title"],
        "domain": raw["domain"],
        "url": page.get("fullurl"),
        "revision_id": page.get("lastrevid"),
        "retrieved_at": raw.get("retrieved_at"),
        "source": raw.get("source"),
        "categories": [
            category["title"]
            for category in page.get(
                "categories",
                []
            )
        ],
        "sections": sections
    }

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            processed,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(
        f"Processed: {page['title']}"
    )


def preprocess():

    Path(
        PROCESSED_ARTICLES_DIR
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    for filepath in sorted(
        RAW_ARTICLES_DIR.glob("*.json")
    ):

        preprocess_article(
            filepath
        )


if __name__ == "__main__":
    preprocess()