# CLAUDE.md — Streaming Marketing Analytics

## Project Overview

This is an analytics engineering portfolio project for ISBA 4715 (Data Analyst). The project targets the **Analyst, Marketing Analytics** role at Paramount+ and builds an end-to-end data pipeline using TMDB content data to answer: *which content attributes define high-performing streaming titles?*

**Student:** Eric Timberlake  
**Repo:** https://github.com/etimber-sys/Media-Marketing-Analyst  
**Course repo (this one):** Contains proposal docs. The project itself lives in the repo above.

---

## Stack

- **Extraction:** Python (`extract/tmdb_extract.py`) hitting the TMDB REST API
- **Warehouse:** Snowflake — database `STREAMING_ANALYTICS`, schemas `RAW`, `STAGING`, `MART`
- **Transformation:** dbt (staging → mart star schema)
- **Orchestration:** GitHub Actions on a daily schedule
- **Dashboard:** Streamlit, deployed to Streamlit Community Cloud
- **Knowledge base:** Claude Code reading from `knowledge/wiki/`

---

## Repo Structure

```
├── docs/               # Proposal PDF, job posting PDF
├── extract/            # Python extraction scripts
├── dbt/                # dbt project (staging + mart models)
├── dashboard/          # Streamlit app
├── knowledge/
│   ├── raw/            # 15+ scraped sources (press releases, earnings transcripts)
│   ├── wiki/           # Claude Code-generated synthesis pages
│   └── index.md        # One-line summaries of all wiki pages
├── .github/workflows/  # GitHub Actions pipelines
├── CLAUDE.md
└── README.md
```

---

## Conventions

- **No credentials in the repo.** All secrets go in `.env` (gitignored) and GitHub Actions secrets. Variables: `TMDB_API_KEY`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_ROLE`.
- **dbt naming:** staging models prefix `stg_`, mart models use full names (`fct_`, `dim_`).
- **Snowflake schema conventions:** raw data lands in `RAW`, dbt staging in `STAGING`, mart in `MART`.
- **Commit style:** short imperative subject line, meaningful message body for non-trivial changes.

---

## Star Schema

**Fact:** `fct_content_performance` — one row per title, with `popularity_score`, `vote_average`, `vote_count`, `content_type` (movie/tv), `release_year`

**Dimensions:**
- `dim_genre` — genre name + content type
- `dim_studio` — studio name + origin country
- `dim_date` — release year, decade, era (classic / streaming era / post-covid)

---

## Business Questions

**Descriptive (what happened?):**
- Which genres have the highest average popularity and vote scores?
- How has content type (movie vs. TV) distribution shifted by decade?
- Which studios produce the most high-rated content?

**Diagnostic (why did it happen?):**
- Do higher vote counts (proxy for reach) correlate with higher ratings?
- Which genre + content type combinations consistently outperform?
- Are newer releases outperforming catalog content, or is the reverse true?

---

## Knowledge Base

### Structure

```
knowledge/
├── raw/           # Scraped sources — Paramount+ press releases, earnings transcripts
├── wiki/
│   ├── overview.md                    # Paramount+ strategy and business context
│   ├── key-entities.md                # Content pillars, subscriber milestones, executives
│   └── content-strategy-synthesis.md  # Cross-source synthesis of content bets
└── index.md       # One-line summaries of all wiki pages
```

### Sources (target: 15+ from 3+ origins)

- Paramount Global investor relations press releases
- Quarterly earnings call transcripts
- Paramount+ content announcement press releases
- Investor Day presentation documents

### How to Query the Knowledge Base

When answering questions about Paramount+, streaming strategy, or content performance context:

1. **Start with `knowledge/index.md`** to find which wiki pages are relevant.
2. **Read the relevant wiki pages** in `knowledge/wiki/` for synthesized insights.
3. **Check `knowledge/raw/`** when a wiki page references a specific source and you need the original detail or quote.
4. **Do not fabricate.** If the knowledge base doesn't contain the answer, say so and note which sources might fill the gap.
5. **Cite sources** by file path when pulling from raw sources.

Example queries you should be able to answer from the knowledge base:
- "What does the knowledge base say about Paramount+'s content strategy for 2025?"
- "Which Paramount+ originals are mentioned as subscriber drivers in the earnings transcripts?"
- "What has leadership said about competing with Netflix on content spend?"

---

## Milestones

| Milestone | Due | Key Deliverables |
|---|---|---|
| Proposal | Apr 13, 2026 | `docs/job-posting.pdf`, `docs/proposal.pdf`, repo initialized |
| Milestone 01 | Apr 27, 2026 | TMDB extract + Snowflake load, dbt staging + mart, GitHub Actions, pipeline diagram |
| Milestone 02 | May 4, 2026 | Web scrape, Streamlit dashboard (deployed), knowledge base, README, ERD, slides |
| Final | May 11, 2026 | `docs/resume.pdf`, final interview demo |
