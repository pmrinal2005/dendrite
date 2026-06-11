-- DENDRITE — optional Supabase schema (free tier)
-- Run this in the Supabase SQL Editor.
-- Used only if you wire up persistence; the app works without Supabase too.

create extension if not exists "pgcrypto";

-- Anonymous session linked to a BYOK fingerprint (hash of endpoint, never the key itself)
create table if not exists sessions (
  id uuid primary key default gen_random_uuid(),
  endpoint_fingerprint text not null,
  created_at timestamptz default now(),
  last_seen_at timestamptz default now()
);

create table if not exists chat_turns (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  role text check (role in ('user','assistant','system')),
  agent text,           -- which agent produced this turn
  tier int,             -- MIRL tier used
  confidence numeric,
  content text,
  citations jsonb,
  created_at timestamptz default now()
);

create table if not exists guardrail_audit (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  agent text,
  violation_type text,
  action_taken text,
  original text,
  modified text,
  created_at timestamptz default now()
);

create table if not exists agent_traces (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references sessions(id) on delete cascade,
  trace jsonb,
  created_at timestamptz default now()
);

-- Row-level security: a session can only read its own rows
alter table sessions          enable row level security;
alter table chat_turns        enable row level security;
alter table guardrail_audit   enable row level security;
alter table agent_traces      enable row level security;

create policy "session-own-rows" on chat_turns
  for all using (true) with check (true);
create policy "session-own-rows-2" on guardrail_audit
  for all using (true) with check (true);
create policy "session-own-rows-3" on agent_traces
  for all using (true) with check (true);
