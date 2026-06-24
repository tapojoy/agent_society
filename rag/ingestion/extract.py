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
    MEDIAWIKI_API,
    USER_AGENT,
    DOMAINS,
    MAX_ARTICLES_PER_DOMAIN,
    RAW_ARTICLES_DIR
)


HEADERS = {
    "User-Agent": USER_AGENT
}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=20)
)
def mediawiki_request(params):
    response = requests.get(
        MEDIAWIKI_API,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def search_articles(domain):

    params = {
        "action": "query",
        "list": "search",
        "srsearch": domain,
        "srlimit": MAX_ARTICLES_PER_DOMAIN,
        "format": "json"
    }

    data = mediawiki_request(params)

    return data["query"]["search"]


def fetch_article(pageid):

    params = {
        "action": "query",
        "prop": "extracts|info|categories",
        "pageids": pageid,
        "explaintext": 1,
        "inprop": "url",
        "cllimit": "max",
        "format": "json"
    }

    data = mediawiki_request(params)

    return data


def save_article(article, domain):

    pages = article["query"]["pages"]

    page = next(iter(pages.values()))

    filename = (
        page["title"]
        .replace("/", "_")
        .replace(" ", "_")
    )

    filepath = (
        RAW_ARTICLES_DIR /
        f"{filename}.json"
    )

    if filepath.exists():
        print(f"Skipping: {page['title']}")
        return

    payload = {
        "domain": domain,
        "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "MediaWiki API",
        "response": article
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"Saved: {page['title']}")


def extract_domain(domain):

    print(f"\n=== {domain} ===")

    results = search_articles(domain)

    for result in results:

        try:

            article = fetch_article(
                result["pageid"]
            )

            save_article(
                article,
                domain
            )

            time.sleep(0.5)

        except Exception as e:

            print(
                f"Failed: "
                f"{result['title']} "
                f"({e})"
            )


def extract():

    Path(RAW_ARTICLES_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    for domain in DOMAINS:
        extract_domain(domain)


if __name__ == "__main__":
    extract()

