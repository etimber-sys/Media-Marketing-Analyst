import os
import requests
from datetime import datetime, timezone
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

TMDB_BASE = 'https://api.themoviedb.org/3'


def fetch_genres(content_type: str, api_key: str) -> list:
    endpoint = 'movie' if content_type == 'movie' else 'tv'
    resp = requests.get(f'{TMDB_BASE}/genre/{endpoint}/list', params={'api_key': api_key})
    resp.raise_for_status()
    return [
        {'genre_id': g['id'], 'genre_name': g['name'], 'content_type': content_type}
        for g in resp.json()['genres']
    ]


def fetch_discover_page(content_type: str, api_key: str, page: int) -> list:
    resp = requests.get(
        f'{TMDB_BASE}/discover/{content_type}',
        params={
            'api_key': api_key,
            'sort_by': 'vote_count.desc',
            'vote_count.gte': 50,
            'page': page,
        },
    )
    resp.raise_for_status()
    return resp.json().get('results', [])


def normalize_content_row(row: dict, content_type: str) -> dict:
    origin = row.get('origin_country', 'US')
    if isinstance(origin, list):
        origin = origin[0] if origin else 'US'

    return {
        'content_id': row['id'],
        'content_type': content_type,
        'title': row.get('title') or row.get('name', ''),
        'popularity': row.get('popularity', 0),
        'vote_average': row.get('vote_average', 0),
        'vote_count': row.get('vote_count', 0),
        'release_date': row.get('release_date') or row.get('first_air_date', ''),
        'genre_ids': ','.join(str(g) for g in row.get('genre_ids', [])),
        'original_language': row.get('original_language', ''),
        'origin_country': origin,
        'extracted_at': datetime.now(timezone.utc).isoformat(),
    }


def _get_conn():
    return snowflake.connector.connect(
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        role=os.environ['SNOWFLAKE_ROLE'],
        schema='RAW',
    )


def _load(cursor, table: str, rows: list, columns: list):
    cursor.execute(f'TRUNCATE TABLE RAW.{table}')
    placeholders = ', '.join(['%s'] * len(columns))
    col_list = ', '.join(columns)
    data = [[row[c] for c in columns] for row in rows]
    cursor.executemany(f'INSERT INTO RAW.{table} ({col_list}) VALUES ({placeholders})', data)
    print(f'Loaded {len(rows)} rows into {table}')


def main():
    api_key = os.environ['TMDB_API_KEY']

    genres = fetch_genres('movie', api_key) + fetch_genres('tv', api_key)
    print(f'Fetched {len(genres)} genres')

    content = []
    for ct in ['movie', 'tv']:
        for page in range(1, 26):
            rows = fetch_discover_page(ct, api_key, page)
            content.extend(normalize_content_row(r, ct) for r in rows)
    print(f'Fetched {len(content)} content rows')

    conn = _get_conn()
    try:
        cur = conn.cursor()
        _load(cur, 'TMDB_GENRES', genres, ['genre_id', 'genre_name', 'content_type'])
        _load(cur, 'TMDB_CONTENT', content, [
            'content_id', 'content_type', 'title', 'popularity',
            'vote_average', 'vote_count', 'release_date', 'genre_ids',
            'original_language', 'origin_country', 'extracted_at',
        ])
        conn.commit()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
