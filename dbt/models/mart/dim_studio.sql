with content as (
    select distinct
        coalesce(origin_country,    'US') as origin_country,
        coalesce(original_language, 'en') as original_language
    from {{ ref('stg_tmdb_content') }}
)

select
    md5(origin_country || '-' || original_language) as studio_sk,
    origin_country,
    original_language
from content
