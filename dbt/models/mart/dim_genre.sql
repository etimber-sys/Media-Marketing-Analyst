with genres as (
    select * from {{ ref('stg_tmdb_genres') }}
)

select
    md5(cast(genre_id as varchar) || '-' || content_type) as genre_sk,
    genre_id,
    genre_name,
    content_type
from genres
