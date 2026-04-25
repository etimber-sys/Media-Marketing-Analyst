with source as (
    select * from {{ source('raw', 'tmdb_genres') }}
),

cleaned as (
    select distinct
        cast(genre_id  as integer) as genre_id,
        trim(genre_name)           as genre_name,
        content_type
    from source
    where genre_name is not null
      and trim(genre_name) != ''
)

select * from cleaned
