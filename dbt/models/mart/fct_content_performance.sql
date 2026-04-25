with content as (
    select * from {{ ref('stg_tmdb_content') }}
)

select
    md5(cast(content_id as varchar) || '-' || content_type) as content_sk,
    content_id,
    content_type,
    title,
    popularity_score,
    vote_average,
    vote_count,
    release_year,
    try_cast(split_part(genre_ids, ',', 1) as integer) as primary_genre_id,
    coalesce(origin_country,    'US') as origin_country,
    coalesce(original_language, 'en') as original_language
from content
