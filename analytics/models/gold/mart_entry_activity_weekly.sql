select user_id, date_trunc('week', entry_date)::date as week_start, count(*) as entry_count, count(distinct entry_date) as active_days
from {{ ref('stg_entries') }}
group by 1, 2
