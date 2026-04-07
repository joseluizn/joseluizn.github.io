import json
import os
import re

from serpapi import GoogleSearch

# ------------------- Configuration -------------------
AUTHOR_ID = '8V-ZZZEAAAAJ'
OUTPUT_PATH = 'src/data/publications.json'
PAGESIZE = 150
BASE_URL = 'https://scholar.google.com/citations'
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise EnvironmentError("SERPAPI_KEY environment variable is not set.")
# -----------------------------------------------------

def fetch_publications(author_id, api_key):
    results = []
    start = 0

    while True:
        params = {
            "engine": "google_scholar_author",
            "hl": "en",
            "author_id": author_id,
            "api_key": api_key,
            "start": start,
            "sort": "pubdate"
        }

        search = GoogleSearch(params)
        data = search.get_dict()

        if "articles" not in data:
            raise ValueError(f"No articles found. Full response: {data}")

        for article in data["articles"]:
            publication = {
                "title": article.get("title"),
                "authors": article.get("authors"),
                "year": article.get("year"),
                "journal": article.get("publication"),
                "link": article.get("link"),
            }
            results.append(publication)

        if "next" not in data.get("pagination", {}):
            break

        start += 100

    return results


def format_publications_json(author_name: re.Pattern, publications):
    """
    Format publications as a list of dicts with highlighted author name.
    Returns a JSON-serializable list.
    """
    result = []
    for pub in sorted(publications, key=lambda x: x['year'], reverse=True):
        author_list = [a.strip() for a in pub['authors'].split(',')]
        authors = [
            f"**{a}**" if re.match(author_name, a) else a
            for a in author_list
        ]
        result.append({
            "title": pub['title'],
            "authors": authors,
            "year": int(pub['year']) if pub['year'] else 0,
            "journal": pub.get('journal') or None,
            "link": pub.get('link') or None,
        })
    return result


def write_json(output_path, data):
    """
    Write publication data as JSON.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated {output_path} successfully.")


if __name__ == '__main__':
    # You may need to supply your name for highlighting
    AUTHOR_NAME = re.compile(r"J(os[eé]|\.)?\s?L(uiz|\.)?\sNunes", re.IGNORECASE)

    pubs = fetch_publications(AUTHOR_ID, SERPAPI_KEY)
    data = format_publications_json(AUTHOR_NAME, pubs)
    write_json(OUTPUT_PATH, data)
