import os
import requests
from datetime import datetime, timezone
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_BASE = 'https://api.firecrawl.dev/v1'

SCRAPE_URLS = [
    'https://ir.paramount.com/news-releases',
    'https://ir.paramount.com/news-releases/news-release-details/paramount-reports-fourth-quarter-and-full-year-2024-results',
    'https://ir.paramount.com/news-releases/news-release-details/paramount-reports-third-quarter-2024-results',
    'https://ir.paramount.com/news-releases/news-release-details/paramount-reports-second-quarter-2024-results',
    'https://ir.paramount.com/news-releases/news-release-details/paramount-reports-first-quarter-2024-results',
    'https://ir.paramount.com/news-releases/news-release-details/paramount-reports-fourth-quarter-and-full-year-2023-results',
    'https://www.paramountpressexpress.com/paramount-plus/',
]


def scrape_url(url: str, api_key: str) -> dict | None:
    resp = requests.post(
        f'{FIRECRAWL_BASE}/scrape',
        headers={'Authorization': f'Bearer {api_key}'},
        json={'url': url, 'formats': ['markdown']},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f'  Skipping {url}: HTTP {resp.status_code}')
        return None
    data = resp.json()
    if not data.get('success'):
        print(f'  Skipping {url}: {data.get("error", "unknown error")}')
        return None
    return data.get('data', {})


def _get_conn():
    return snowflake.connector.connect(
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        role=os.environ['SNOWFLAKE_ROLE'],
    )


def _setup(cursor):
    db = os.environ['SNOWFLAKE_DATABASE']
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {db}.RAW.WEB_CONTENT (
            url            VARCHAR(2000),
            title          VARCHAR(1000),
            content        TEXT,
            source_domain  VARCHAR(200),
            scraped_at     TIMESTAMP
        )
    ''')


def _load(cursor, rows: list):
    db = os.environ['SNOWFLAKE_DATABASE']
    cursor.execute(f'TRUNCATE TABLE {db}.RAW.WEB_CONTENT')
    cursor.executemany(
        f'INSERT INTO {db}.RAW.WEB_CONTENT (url, title, content, source_domain, scraped_at) VALUES (%s, %s, %s, %s, %s)',
        [[r['url'], r['title'], r['content'], r['source_domain'], r['scraped_at']] for r in rows],
    )
    print(f'Loaded {len(rows)} pages into WEB_CONTENT')


def main():
    api_key = os.environ['FIRECRAWL_API_KEY']
    rows = []

    for url in SCRAPE_URLS:
        print(f'Scraping {url}')
        data = scrape_url(url, api_key)
        if not data:
            continue
        metadata = data.get('metadata', {})
        rows.append({
            'url': url,
            'title': (metadata.get('title') or metadata.get('ogTitle') or '')[:1000],
            'content': (data.get('markdown') or '')[:50000],
            'source_domain': url.split('/')[2],
            'scraped_at': datetime.now(timezone.utc).isoformat(),
        })
        print(f'  OK — {len(data.get("markdown", ""))} chars')

    if not rows:
        print('No pages scraped successfully')
        return

    conn = _get_conn()
    try:
        cur = conn.cursor()
        _setup(cur)
        _load(cur, rows)
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
