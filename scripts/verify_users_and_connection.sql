-- Run in Supabase → SQL Editor (same project you expect the app to use).
-- If row counts differ from what you see in the app, DATABASE_URL points elsewhere.

select current_database() as database_name,
       current_user as connected_role;

select count(*) as rows_in_public_users from public.users;

select id, email, created_at
from public.users
order by id desc
limit 20;
