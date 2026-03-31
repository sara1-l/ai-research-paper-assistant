-- Run once in Supabase: SQL Editor → New query → Run
-- Needed if your app uses the transaction pooler (port 6543), which often cannot run DDL.

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON public.users (email);
