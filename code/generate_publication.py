import os
import re
import requests
from collections import defaultdict

from bs4 import BeautifulSoup
from serpapi import GoogleSearch

# ------------------- Configuration -------------------
AUTHOR_ID = '8V-ZZZEAAAAJ'
TEMPLATE_PATH = 'publications.qmd'
OUTPUT_PATH = '../publications.qmd'
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


def format_publications_markdown(author_name: re.Pattern, publications):
    """
    Group publications by year, descending, and highlight the author_name.
    Returns a Markdown-formatted string.
    """
    # Sort publications descending by year
    pubs = sorted(publications, key=lambda x: x['year'], reverse=True)

    # Group by year
    by_year = defaultdict(list)
    for pub in pubs:
        by_year[pub['year']].append(pub)

    lines = []
    for year in sorted(by_year.keys(), reverse=True):
        label = 'Unknown' if year == 0 else str(year)
        lines.append(f"### {label}")
        for pub in by_year[year]:
            # Title link
            title_md = f"[{pub['title']}]({pub['link']})" if pub.get('link') else pub['title']

            # Highlight author_name
            author_list = [a.strip() for a in pub['authors'].split(',')]
            authors_md = ', '.join([
                "**José Luiz Nunes**" if re.match(author_name, a) else a
                for a in author_list
            ])

            lines.append(f"- {title_md}  ")
            lines.append(f"  *{authors_md}*  ")
            if pub.get('journal'):
                lines.append(f"  *{pub['journal']}*  ")
        lines.append('')

    return '\n'.join(lines)


def update_template(template_path, output_path, content):
    """
    Replace everything after the marker in the template and save to output.
    """
    marker = '<!-- Publications to be added below: -->'
    with open(template_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Locate marker
    for i, line in enumerate(lines):
        if marker in line:
            idx = i + 1
            break
    else:
        raise RuntimeError(f"Marker '{marker}' not found in template.")

    new_lines = lines[:idx] + ['\n'] + [content]
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Generated {output_path} successfully.")


if __name__ == '__main__':
    # You may need to supply your name for highlighting
    AUTHOR_NAME = re.compile(r"J(os[eé]|\.)?\s?L(uiz|\.)?\sNunes", re.IGNORECASE)

    pubs = fetch_publications(AUTHOR_ID, SERPAPI_KEY)
    md = format_publications_markdown(AUTHOR_NAME, pubs)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    update_template(TEMPLATE_PATH, OUTPUT_PATH, md)
