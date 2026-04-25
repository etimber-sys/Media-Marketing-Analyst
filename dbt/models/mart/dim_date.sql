with years as (
    select distinct release_year
    from {{ ref('stg_tmdb_content') }}
    where release_year is not null
)

select
    release_year,
    cast(floor(release_year / 10) * 10 as varchar) || 's' as decade,
    case
        when release_year < 1990 then 'classic'
        when release_year < 2020 then 'streaming era'
        else 'post-covid'
    end as era
from years
