import os
import pytest
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def conn():
    c = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )
    yield c
    c.close()


def test_fct_content_performance_not_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM STREAMING_ANALYTICS.MART.fct_content_performance")
    assert cur.fetchone()[0] > 0


def test_dim_genre_not_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM STREAMING_ANALYTICS.MART.dim_genre")
    assert cur.fetchone()[0] > 0


def test_dim_date_not_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM STREAMING_ANALYTICS.MART.dim_date")
    assert cur.fetchone()[0] > 0


def test_fct_has_expected_columns(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT content_sk, content_type, title, popularity_score,
               vote_average, vote_count, release_year, primary_genre_id
        FROM STREAMING_ANALYTICS.MART.fct_content_performance
        LIMIT 1
    """)
    cols = {d[0].lower() for d in cur.description}
    assert cols == {
        "content_sk", "content_type", "title", "popularity_score",
        "vote_average", "vote_count", "release_year", "primary_genre_id",
    }


def test_genre_join_works(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT g.genre_name, COUNT(*) as cnt
        FROM STREAMING_ANALYTICS.MART.fct_content_performance f
        JOIN STREAMING_ANALYTICS.MART.dim_genre g
            ON f.primary_genre_id = g.genre_id AND f.content_type = g.content_type
        GROUP BY g.genre_name
        ORDER BY cnt DESC
        LIMIT 5
    """)
    rows = cur.fetchall()
    assert len(rows) > 0


def test_date_join_works(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT d.era, COUNT(*) as cnt
        FROM STREAMING_ANALYTICS.MART.fct_content_performance f
        JOIN STREAMING_ANALYTICS.MART.dim_date d ON f.release_year = d.release_year
        GROUP BY d.era
    """)
    rows = cur.fetchall()
    eras = {r[0] for r in rows}
    assert eras == {"classic", "streaming era", "post-covid"}
