---
marp: true
theme: default
paginate: true
style: |
  section { font-family: 'Segoe UI', sans-serif; }
  h1 { color: #003087; }
  h2 { color: #003087; }
  table { font-size: 0.85em; }
  code { font-size: 0.8em; }
---

# Streaming Marketing Analytics
## Paramount+ Content Performance Analysis

**Eric Timberlake**
ISBA 4715 — Data Analyst | May 2026

---

# Business Question

> **Which content attributes define high-performing streaming titles — and what does that tell Paramount+ about where to invest?**

**Data source:** TMDB (The Movie Database)
**Scope:** 2,500+ movies and TV shows with 50+ votes
**Pipeline:** TMDB API → Snowflake RAW → dbt STAGING → dbt MART → Streamlit

**Target role:** Analyst, Marketing Analytics @ Paramount+

---

# Data Pipeline

```
TMDB API ──────────────► tmdb_extract.py ────────► Snowflake RAW
Paramount IR/Press ────► firecrawl_extract.py ───► Snowflake RAW
                                                         │
                                               dbt staging models
                                               (stg_tmdb_content,
                                                stg_tmdb_genres)
                                                         │
                                                dbt mart — star schema
                                                (fct + 3 dimensions)
                                                         │
                                             Streamlit Dashboard
                                           (deployed: Community Cloud)
```

**Orchestration:** GitHub Actions — daily scheduled pipeline run

---

# Star Schema

```
fct_content_performance
├── content_sk (PK)           ┌── dim_genre
├── content_type              │   ├── genre_sk (PK)
├── title                     │   ├── genre_name
├── popularity_score          │   └── content_type
├── vote_average              │
├── vote_count                ├── dim_date
├── release_year ─────────────┤   ├── release_year (PK)
├── primary_genre_id ─────────┤   ├── decade
├── origin_country ───────────┤   └── era (classic / streaming / post-covid)
└── original_language         │
                              └── dim_studio
                                  ├── studio_sk (PK)
                                  ├── origin_country
                                  └── original_language
```

---

# Insight 1 — Genre Popularity

**Action and Drama dominate popularity across both movies and TV**

| Genre | Signal | Finding |
|---|---|---|
| Action | Popularity | Highest average popularity score — drives algorithmic reach |
| Drama | Popularity + Rating | Top in both volume and vote average |
| Documentary | Vote Average | Leads in quality signal despite lower popularity |
| History | Vote Average | Punches above its weight on audience satisfaction |

**So what:** Paramount+ should prioritize Action and Drama originals to maximize subscriber acquisition; Documentary/History investment yields quality credibility with niche audiences.

---

# Insight 2 — Movie vs. TV Shift

**TV's share of high-performing content has grown every decade since 1990**

- **Pre-streaming (pre-2010):** movies dominate title volume and popularity
- **Streaming era (2010–2019):** TV rises sharply in both volume and popularity score
- **Post-COVID (2020+):** TV content accounts for the majority of top-popularity titles; movie volume declines relative to TV

**So what:** Investing in serialized TV originals — especially franchise-driven series — aligns with both audience behavior and Paramount+'s subscription retention playbook (Yellowstone, Sheridan universe, Star Trek).

---

# Insight 3 — Catalog vs. New Releases

**Post-COVID titles outperform catalog on popularity — but catalog wins on ratings**

| Era | Signal | Pattern |
|---|---|---|
| Classic (pre-1990) | Vote Average | Highest ratings — surviving catalog earns sustained quality scores |
| Streaming Era (2010–2019) | Balanced | Middle ground on both metrics |
| Post-COVID (2020+) | Popularity Score | Newest content benefits most from algorithmic exposure |

**So what:** Marketing spend allocation should differ by goal — amplify new originals for subscriber acquisition; surface high-rated classic catalog for engagement and retention.

---

# Insight 4 — Reach vs. Quality

**Vote count (reach) and vote average (quality) are largely independent signals**

- Pearson r ≈ 0.1–0.2 — weak positive correlation overall
- Higher vote counts do not reliably predict higher ratings
- Non-English content (Korean `ko`, Japanese `ja`, Spanish `es`) leads in vote average despite lower global vote counts — quality punches above reach

**So what:** Reach and quality require different marketing levers. High vote-count titles need reach amplification; high-rated low-reach titles need awareness campaigns to convert latent quality into subscriber acquisition.

---

# Insight 5 — International Content Quality

**Non-English originals outperform English content on audience satisfaction**

| Language | Pattern |
|---|---|
| Korean (`ko`) | Consistently top vote averages — Squid Game effect |
| Japanese (`ja`) | Strong ratings across anime and drama |
| Spanish (`es`) | High engagement; growing global audience |
| English (`en`) | Dominates volume but middle-of-pack on vote average |

**So what:** Co-productions and acquisitions from Korea, Japan, and Spain represent a high-quality, potentially lower-cost path to content differentiation — directly relevant to Paramount+'s international expansion thesis.

---

# Recommendations for Paramount+

1. **Prioritize Action and Drama TV originals** — this genre-type combination has the highest average popularity score and aligns with the Sheridan universe franchise model (Yellowstone, Landman, 1923).

2. **Differentiate reach vs. quality in media spend** — allocate performance marketing budget toward new originals for subscriber acquisition; allocate content marketing budget toward surfacing high-rated catalog titles for retention.

3. **Expand international co-production pipeline** — Korean and Japanese originals consistently outperform on quality metrics. The data supports pursuing more titles in these markets alongside Paramount+'s existing English-language dominance.

---

# Knowledge Base

Paramount+ strategy context drawn from **17 scraped sources** across 3 domains:

| Source Type | Key Findings |
|---|---|
| Paramount Global IR (9 quarterly earnings) | Subscriber trajectory 100K (2015) → 79M (2025); DTC profitability focus post-2023 |
| Paramount Press Express | Taylor Sheridan universe as #1 franchise bet; The Madison (8M views debut); sports rights (NFL, UFC, UEFA) |
| Wikipedia (8 pages) | Full competitive context: streaming wars, SVOD model, platform history, brand portfolio |

**Connection to TMDB analysis:** Data confirms Paramount+'s stated bets — Action/Drama TV dominance, post-COVID popularity surge, international quality opportunity.

---

# Portfolio Summary

**Project:** Streaming Marketing Analytics — Paramount+
**Repo:** github.com/etimber-sys/Media-Marketing-Analyst

| Skill | Demonstrated |
|---|---|
| SQL + Data Modeling | dbt star schema — 1 fact table, 3 dimensions |
| Pipeline Engineering | Python extract, Snowflake load, GitHub Actions daily schedule |
| Analytics | 6 descriptive + diagnostic business questions answered |
| Visualization | Streamlit + Plotly — 4 tabs, interactive filters |
| Domain Knowledge | 17 Paramount+ sources, 3 wiki synthesis pages |

**Target role:** Analyst, Marketing Analytics @ Paramount+
