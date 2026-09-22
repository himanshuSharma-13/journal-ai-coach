select id as entry_id, user_id, occurred_at::date as entry_date, content, source, created_at, updated_at
from public.journal_entries
where length(trim(content)) >= 20
