import os
import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

# ------------------- Configuration -------------------
AUTHOR_ID = '8V-ZZZEAAAAJ'
TEMPLATE_PATH = 'publications.qmd'
OUTPUT_PATH = '../publications.qmd'
PAGESIZE = 200
BASE_URL = 'https://scholar.google.com/citations'
# -----------------------------------------------------


def fetch_publications(author_id):
    """
    Fetch all publications from Google Scholar using requests and BeautifulSoup.
    Returns a list of dicts with keys: year, title, authors, venue, url.
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36'
    })
    publications = []
    start = 0

    while True:
        params = {
            'hl': 'en',
            'user': author_id,
            'sortby': 'pubdate',
            'cstart': start,
            'pagesize': PAGESIZE
        }
        response = session.get(BASE_URL, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.find_all('tr', class_='gsc_a_tr')
        if not rows:
            break

        for row in rows:
            # Title and URL
            title_tag = row.find('a', class_='gsc_a_at')
            title = title_tag.text.strip() if title_tag else ''
            url = 'https://scholar.google.com' + title_tag['href'] if title_tag and title_tag.has_attr('href') else ''

            # Authors and venue
            gs_gray = row.find_all('div', class_='gs_gray')
            authors = gs_gray[0].text.strip() if len(gs_gray) > 0 else ''
            venue = gs_gray[1].text.strip() if len(gs_gray) > 1 else ''

            # Year
            year_tag = row.find('span', class_='gsc_a_h')
            year_text = year_tag.text.strip() if year_tag else ''
            try:
                year = int(year_text)
            except ValueError:
                year = 0

            publications.append({
                'year': year,
                'title': title,
                'authors': authors,
                'venue': venue,
                'url': url
            })

        # If fewer than a full page, we're done
        if len(rows) < PAGESIZE:
            break
        start += PAGESIZE

    return publications


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
            title_md = f"[{pub['title']}]({pub['url']})" if pub['url'] else pub['title']

            # Highlight author_name
            author_list = [a.strip() for a in pub['authors'].split(',')]
            authors_md = ', '.join([
                "**José Luiz Nunes**" if re.match(author_name, a) else a
                for a in author_list
            ])

            lines.append(f"- {title_md}  ")
            lines.append(f"  *{authors_md}*  ")
            if pub['venue']:
                lines.append(f"  *{pub['venue']}*  ")
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

    pubs = fetch_publications(AUTHOR_ID)
    md = format_publications_markdown(AUTHOR_NAME, pubs)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    update_template(TEMPLATE_PATH, OUTPUT_PATH, md)
