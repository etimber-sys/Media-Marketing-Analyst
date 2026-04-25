import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'extract'))

from unittest.mock import patch, MagicMock
import pytest


def test_normalize_content_row_movie():
    from tmdb_extract import normalize_content_row
    row = {
        'id': 123,
        'title': 'Test Movie',
        'popularity': 45.2,
        'vote_average': 7.5,
        'vote_count': 1000,
        'release_date': '2022-06-15',
        'genre_ids': [28, 12],
        'original_language': 'en',
    }
    result = normalize_content_row(row, 'movie')
    assert result['content_id'] == 123
    assert result['content_type'] == 'movie'
    assert result['title'] == 'Test Movie'
    assert result['genre_ids'] == '28,12'
    assert result['origin_country'] == 'US'
    assert result['release_date'] == '2022-06-15'


def test_normalize_content_row_tv():
    from tmdb_extract import normalize_content_row
    row = {
        'id': 456,
        'name': 'Test Show',
        'popularity': 30.1,
        'vote_average': 8.0,
        'vote_count': 500,
        'first_air_date': '2021-01-10',
        'genre_ids': [18],
        'original_language': 'en',
        'origin_country': ['GB'],
    }
    result = normalize_content_row(row, 'tv')
    assert result['content_id'] == 456
    assert result['content_type'] == 'tv'
    assert result['title'] == 'Test Show'
    assert result['origin_country'] == 'GB'
    assert result['release_date'] == '2021-01-10'


def test_normalize_content_row_empty_genre_ids():
    from tmdb_extract import normalize_content_row
    row = {
        'id': 789,
        'title': 'No Genres',
        'popularity': 10.0,
        'vote_average': 6.0,
        'vote_count': 100,
        'release_date': '2020-01-01',
        'genre_ids': [],
        'original_language': 'fr',
    }
    result = normalize_content_row(row, 'movie')
    assert result['genre_ids'] == ''
    assert result['origin_country'] == 'US'


def test_fetch_genres_returns_normalized_list():
    from tmdb_extract import fetch_genres
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'genres': [
            {'id': 28, 'name': 'Action'},
            {'id': 12, 'name': 'Adventure'},
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('requests.get', return_value=mock_response):
        result = fetch_genres('movie', 'fake_key')

    assert len(result) == 2
    assert result[0] == {'genre_id': 28, 'genre_name': 'Action', 'content_type': 'movie'}
    assert result[1] == {'genre_id': 12, 'genre_name': 'Adventure', 'content_type': 'movie'}
