with source as (
    select * from {{ source('raw', 'tmdb_content') }}
),

cleaned as (
    select
        content_id,
        content_type,
        title,
        cast(popularity   as float)   as popularity_score,
        cast(vote_average as float)   as vote_average,
        cast(vote_count   as integer) as vote_count,
        try_to_date(release_date, 'YYYY-MM-DD')        as release_date,
        year(try_to_date(release_date, 'YYYY-MM-DD'))  as release_year,
        genre_ids,
        original_language,
        nullif(trim(origin_country), '') as origin_country,
        extracted_at
    from source
    where release_date is not null
      and release_date != ''
      and vote_count > 0
)

select * from cleaned
