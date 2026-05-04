# Milestone 02 Design — Present & Polish

**Date:** 2026-05-03  
**Due:** 2026-05-04  
**Student:** Eric Timberlake  
**Deliverables:** Steps 6–14 (steps 6, 8, 9 already complete)

---

## Scope

Remaining work to complete Milestone 02:

| Step | Deliverable | Pts | Status |
|---|---|---|---|
| 7 | Streamlit dashboard (deployed) | 15 | Build |
| 10 | Presentation slides (PDF) | 7 | Build |
| 11 | Knowledge base | 8 | Build |
| 12 | README updates | 5 | Partial |
| 13 | ERD | 3 | Build |

**Execution order:** Knowledge base → Dashboard → Slides → ERD → README

---

## 1. Knowledge Base

### Goal
15+ raw markdown files in `knowledge/raw/` from 3+ distinct domains, Claude Code-generated wiki pages in `knowledge/wiki/`, and a `knowledge/index.md` index.

### Sources (15 total, 3 domains)

**`ir.paramount.com` — 9 pages**
- `news-releases` index
- Q4 + full year 2024 results
- Q3 2024 results
- Q2 2024 results
- Q1 2024 results
- Q4 + full year 2023 results
- Q3 2023 results
- Q2 2023 results
- Q1 2023 results

**`paramountpressexpress.com` — 2 pages**
- `/paramount-plus/`
- `/paramount-global/`

**`en.wikipedia.org` — 4 pages**
- Paramount+
- Paramount Global
- Streaming wars
- Subscription video on demand

### File naming
`knowledge/raw/<domain>-<slug>.md` — e.g., `ir-paramount-q4-2024.md`, `wikipedia-paramount-plus.md`

### Wiki pages
| File | Content |
|---|---|
| `knowledge/wiki/overview.md` | Paramount+ strategy and business context |
| `knowledge/wiki/key-entities.md` | Content pillars, subscriber milestones, executives |
| `knowledge/wiki/content-strategy-synthesis.md` | Cross-source synthesis of content bets |
| `knowledge/index.md` | One-line summary per wiki page + raw source list |

---

## 2. Streamlit Dashboard

### File
`dashboard/app.py` + `dashboard/requirements.txt`

### Architecture
- Connects to Snowflake `STREAMING_ANALYTICS.MART` via `snowflake-connector-python`
- Credentials: `st.secrets` on Streamlit Community Cloud, `.env` locally
- Single-page layout with sidebar filters

### Sidebar Filters
- Content type: Movie / TV / All
- Era: Classic / Streaming Era / Post-COVID / All

### Section 1 — Descriptive (what happened?)
| Chart | Type | Source table |
|---|---|---|
| Average popularity score by genre | Horizontal bar, sorted desc | `fct_content_performance` + `dim_genre` |
| Content type distribution by decade | Stacked bar | `fct_content_performance` + `dim_date` |
| Top 15 studios by average vote average | Bar chart | `fct_content_performance` + `dim_studio` |

### Section 2 — Diagnostic (why did it happen?)
| Chart | Type | Source table |
|---|---|---|
| Vote count vs. vote average | Scatter, colored by content type | `fct_content_performance` |
| Top genre + content type combos by popularity | Grouped bar | `fct_content_performance` + `dim_genre` |
| Average popularity by era | Bar chart | `fct_content_performance` + `dim_date` |

All charts respond to sidebar filters.

### Deployment
Push to GitHub → connect to Streamlit Community Cloud → add Snowflake credentials as secrets (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_ROLE`).

---

## 3. Presentation Slides

### File
`docs/slides.md` (Markdown) → exported to PDF for Brightspace

### Structure (10 slides)
1. **Title** — project name, Eric Timberlake, Analyst Marketing Analytics @ Paramount+
2. **Business question** — which content attributes define high-performing streaming titles?
3. **Data pipeline** — architecture overview, tools
4. **Insight 1 (Descriptive)** — genre popularity rankings + takeaway
5. **Insight 2 (Descriptive)** — movie vs. TV shift by decade + takeaway
6. **Insight 3 (Descriptive)** — top studios by rating + takeaway
7. **Insight 4 (Diagnostic)** — vote count vs. vote average correlation
8. **Insight 5 (Diagnostic)** — genre + content type combos that consistently outperform
9. **Recommendations** — 3 bullet points for Paramount+ content investment
10. **Portfolio summary** — tech stack, repo link, skills demonstrated

Each insight slide: chart description placeholder + one-sentence "so what." Numbers filled in after dashboard is live.

---

## 4. ERD

### Approach
Mermaid `erDiagram` block generated from `dbt/models/mart/schema.yml` and `dbt/models/staging/schema.yml`. Embedded in `README.md`.

### Tables
- `fct_content_performance` (center) — `tmdb_id`, `title`, `popularity_score`, `vote_average`, `vote_count`, `content_type`, `release_year`, `genre_id`, `studio_id`, `date_id`
- `dim_genre` — `genre_id`, `genre_name`, `content_type`
- `dim_studio` — `studio_id`, `studio_name`, `origin_country`
- `dim_date` — `date_id`, `release_year`, `decade`, `era`

---

## 5. README Updates

### Changes
- Replace `> ERD to be generated...` placeholder with the Mermaid ERD block
- Fill in **Key Insights** section with 3–4 bullet points (placeholders first, real numbers after dashboard)
- Update repo structure block to include `dashboard/app.py`, `extract/firecrawl_extract.py`, `knowledge/`
