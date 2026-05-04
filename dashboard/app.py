import os
import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Streaming Analytics — Paramount+",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Snowflake connection ──────────────────────────────────────────────────────

def _creds() -> dict:
    try:
        s = st.secrets["snowflake"]
        return dict(
            account=s["account"], user=s["user"], password=s["password"],
            database=s["database"], warehouse=s["warehouse"], role=s["role"],
        )
    except Exception:
        return dict(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            role=os.environ["SNOWFLAKE_ROLE"],
        )


@st.cache_data(ttl=3600, show_spinner="Loading from Snowflake…")
def _query(sql: str) -> pd.DataFrame:
    conn = snowflake.connector.connect(**_creds())
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


# ── SQL ───────────────────────────────────────────────────────────────────────

_GENRE_SQL = """
SELECT
    g.genre_name,
    f.content_type,
    COUNT(*)                          AS title_count,
    ROUND(AVG(f.popularity_score), 2) AS avg_popularity,
    ROUND(AVG(f.vote_average), 2)     AS avg_vote_avg,
    ROUND(AVG(f.vote_count), 0)       AS avg_vote_count
FROM STREAMING_ANALYTICS.MART.fct_content_performance f
JOIN STREAMING_ANALYTICS.MART.dim_genre g
    ON f.primary_genre_id = g.genre_id AND f.content_type = g.content_type
GROUP BY g.genre_name, f.content_type
ORDER BY avg_popularity DESC
"""

_DECADE_SQL = """
SELECT
    d.decade,
    d.era,
    f.content_type,
    COUNT(*)                          AS title_count,
    ROUND(AVG(f.popularity_score), 2) AS avg_popularity,
    ROUND(AVG(f.vote_average), 2)     AS avg_vote_avg
FROM STREAMING_ANALYTICS.MART.fct_content_performance f
JOIN STREAMING_ANALYTICS.MART.dim_date d ON f.release_year = d.release_year
GROUP BY d.decade, d.era, f.content_type
ORDER BY d.decade, f.content_type
"""

_ERA_SQL = """
SELECT
    d.era,
    f.content_type,
    COUNT(*)                          AS title_count,
    ROUND(AVG(f.popularity_score), 2) AS avg_popularity,
    ROUND(AVG(f.vote_average), 2)     AS avg_vote_avg
FROM STREAMING_ANALYTICS.MART.fct_content_performance f
JOIN STREAMING_ANALYTICS.MART.dim_date d ON f.release_year = d.release_year
GROUP BY d.era, f.content_type
"""

_SCATTER_SQL = """
SELECT
    f.title,
    f.content_type,
    f.vote_count,
    f.vote_average,
    f.popularity_score,
    f.release_year,
    g.genre_name
FROM STREAMING_ANALYTICS.MART.fct_content_performance f
LEFT JOIN STREAMING_ANALYTICS.MART.dim_genre g
    ON f.primary_genre_id = g.genre_id AND f.content_type = g.content_type
WHERE f.vote_count > 50
LIMIT 3000
"""

_LANG_SQL = """
SELECT
    original_language,
    content_type,
    COUNT(*)                          AS title_count,
    ROUND(AVG(popularity_score), 2)   AS avg_popularity,
    ROUND(AVG(vote_average), 2)       AS avg_vote_avg
FROM STREAMING_ANALYTICS.MART.fct_content_performance
GROUP BY original_language, content_type
HAVING COUNT(*) >= 5
ORDER BY avg_popularity DESC
"""

# ── Color palette ─────────────────────────────────────────────────────────────
TYPE_COLORS = {"movie": "#0066CC", "tv": "#FF6B35"}
ERA_ORDER   = ["classic", "streaming era", "post-covid"]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Streaming Marketing Analytics")
st.caption(
    "TMDB content data · Snowflake MART schema · "
    "ISBA 4715 — targeting Analyst, Marketing Analytics @ Paramount+"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Filters")
content_filter = st.sidebar.radio("Content Type", ["All", "movie", "tv"])
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data source:** TMDB REST API  \n"
    "**Pipeline:** Python → Snowflake → dbt  \n"
    "**Refresh:** daily via GitHub Actions"
)

def _apply_filter(df: pd.DataFrame) -> pd.DataFrame:
    if content_filter != "All":
        return df[df["content_type"] == content_filter]
    return df


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Genre Performance",
    "Content Trends by Era",
    "Reach vs. Quality",
    "Language & Origin",
])

# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Genre Performance
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    df_genre = _apply_filter(_query(_GENRE_SQL))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Genres by Popularity")
        top_pop = (
            df_genre.groupby("genre_name", as_index=False)["avg_popularity"]
            .mean()
            .sort_values("avg_popularity", ascending=False)
            .head(15)
        )
        fig = px.bar(
            top_pop, x="avg_popularity", y="genre_name", orientation="h",
            color="avg_popularity", color_continuous_scale="Blues",
            labels={"avg_popularity": "Avg Popularity Score", "genre_name": "Genre"},
        )
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top Genres by Audience Rating")
        top_vote = (
            df_genre[df_genre["avg_vote_count"] >= 100]
            .groupby("genre_name", as_index=False)["avg_vote_avg"]
            .mean()
            .sort_values("avg_vote_avg", ascending=False)
            .head(15)
        )
        fig2 = px.bar(
            top_vote, x="avg_vote_avg", y="genre_name", orientation="h",
            color="avg_vote_avg", color_continuous_scale="Greens",
            labels={"avg_vote_avg": "Avg Vote Average", "genre_name": "Genre"},
        )
        fig2.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Genre × Content Type Heatmap")
    df_all_genre = _query(_GENRE_SQL)  # always use both types for heatmap
    pivot = df_all_genre.pivot_table(
        index="genre_name", columns="content_type",
        values="avg_popularity", aggfunc="mean",
    ).fillna(0)
    pivot = pivot.sort_values(by=pivot.columns[0], ascending=False)
    fig3 = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        labels={"color": "Avg Popularity"},
        aspect="auto",
        title="Which genre + content type combinations consistently outperform?",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Content Trends by Era
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    df_decade = _apply_filter(_query(_DECADE_SQL))
    df_era    = _apply_filter(_query(_ERA_SQL))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Title Volume by Decade")
        fig = px.bar(
            df_decade, x="decade", y="title_count", color="content_type",
            barmode="group",
            color_discrete_map=TYPE_COLORS,
            labels={"title_count": "# Titles", "decade": "Decade", "content_type": "Type"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Popularity by Decade")
        fig2 = px.line(
            df_decade, x="decade", y="avg_popularity", color="content_type",
            markers=True,
            color_discrete_map=TYPE_COLORS,
            labels={
                "avg_popularity": "Avg Popularity",
                "decade": "Decade",
                "content_type": "Type",
            },
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Era Comparison")

    df_era["era"] = pd.Categorical(df_era["era"], categories=ERA_ORDER, ordered=True)
    df_era = df_era.sort_values("era")

    metric_cols = st.columns(3)
    for i, era in enumerate(ERA_ORDER):
        subset = df_era[df_era["era"] == era]
        if not subset.empty:
            metric_cols[i].metric(era.title(), f"{int(subset['title_count'].sum()):,} titles")
            metric_cols[i].metric("Avg Popularity", f"{subset['avg_popularity'].mean():.1f}")
            metric_cols[i].metric("Avg Vote Avg",   f"{subset['avg_vote_avg'].mean():.2f}")

    fig3 = px.bar(
        df_era, x="era", y="avg_popularity", color="content_type",
        barmode="group",
        category_orders={"era": ERA_ORDER},
        color_discrete_map=TYPE_COLORS,
        labels={
            "avg_popularity": "Avg Popularity",
            "era": "Era",
            "content_type": "Type",
        },
        title="Are newer releases outperforming catalog content?",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Reach vs. Quality
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    df_scatter = _apply_filter(_query(_SCATTER_SQL))

    st.subheader("Vote Count vs. Vote Average")
    st.caption(
        "Each point is a title. Bubble size = popularity score. "
        "Titles with fewer than 50 votes excluded. X-axis is log scale."
    )

    fig = px.scatter(
        df_scatter,
        x="vote_count", y="vote_average",
        color="content_type",
        size="popularity_score",
        hover_data=["title", "release_year", "genre_name"],
        log_x=True,
        opacity=0.55,
        color_discrete_map=TYPE_COLORS,
        labels={
            "vote_count":      "Vote Count (log scale)",
            "vote_average":    "Vote Average",
            "content_type":    "Type",
            "popularity_score": "Popularity",
        },
    )
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True)

    if len(df_scatter) >= 2:
        corr = df_scatter[["vote_count", "vote_average"]].corr().iloc[0, 1]
        if corr > 0.3:
            st.success(
                f"Pearson r = **{corr:.3f}** — moderate positive correlation: "
                "titles with broader audiences tend to earn higher ratings."
            )
        elif corr < -0.1:
            st.warning(
                f"Pearson r = **{corr:.3f}** — inverse relationship: "
                "niche titles with fewer votes may skew higher in ratings."
            )
        else:
            st.info(
                f"Pearson r = **{corr:.3f}** — vote count and vote average "
                "are largely independent signals in this dataset."
            )

# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Language & Origin
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    df_lang = _apply_filter(_query(_LANG_SQL))

    st.subheader("Average Popularity by Original Language")
    st.caption("Languages with fewer than 5 titles excluded.")

    top_pop_lang = (
        df_lang.groupby("original_language", as_index=False)["avg_popularity"]
        .mean()
        .sort_values("avg_popularity", ascending=False)
        .head(20)
    )
    fig = px.bar(
        top_pop_lang, x="original_language", y="avg_popularity",
        color="avg_popularity", color_continuous_scale="Purples",
        labels={"avg_popularity": "Avg Popularity", "original_language": "Language Code"},
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Title Share by Language")
        lang_count = (
            df_lang.groupby("original_language", as_index=False)["title_count"]
            .sum()
            .sort_values("title_count", ascending=False)
            .head(12)
        )
        fig2 = px.pie(
            lang_count, names="original_language", values="title_count",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Vote Average by Language")
        top_vote_lang = (
            df_lang.groupby("original_language", as_index=False)["avg_vote_avg"]
            .mean()
            .sort_values("avg_vote_avg", ascending=False)
            .head(15)
        )
        fig3 = px.bar(
            top_vote_lang, x="avg_vote_avg", y="original_language",
            orientation="h",
            color="avg_vote_avg", color_continuous_scale="Greens",
            labels={"avg_vote_avg": "Avg Vote Average", "original_language": "Language"},
        )
        fig3.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig3, use_container_width=True)
