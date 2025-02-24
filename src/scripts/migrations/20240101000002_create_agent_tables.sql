-- Create agent-related tables for tracking queries and responses
-- Migration: 20240101000002_create_agent_tables

-- Enable necessary extensions
create extension if not exists "pg_trgm";  -- For text search

-- Create enums for agent types and query types
create type agent_type as enum (
    'customer_support',
    'product_specialist'
);

create type query_type as enum (
    'general',
    'product_comparison',
    'technical_question',
    'feature_inquiry',
    'compatibility_check'
);

-- Create table for agent queries
create table if not exists agent_queries (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    session_id uuid not null,
    
    -- Query details
    query_text text not null,
    query_type query_type not null,
    query_hash text not null,  -- For caching
    focus_areas text[] not null default array[]::text[],
    model_numbers text[] not null default array[]::text[],
    
    -- Context and metadata
    context jsonb not null default '{}'::jsonb,
    confidence float not null check (confidence >= 0 and confidence <= 1),
    requires_specialist boolean not null default false,
    specialist_type agent_type,
    
    -- Timestamps and tracking
    created_at timestamp with time zone not null default now(),
    response_time interval,
    
    -- Constraints
    constraint valid_query_text check (length(query_text) > 0),
    constraint valid_context check (jsonb_typeof(context) = 'object')
);

-- Create table for agent responses
create table if not exists agent_responses (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    query_id uuid not null references agent_queries(id),
    agent_type agent_type not null,
    
    -- Response content
    response_data jsonb not null,
    confidence float not null check (confidence >= 0 and confidence <= 1),
    
    -- Analysis details
    technical_analysis text,
    recommendations text[] not null default array[]::text[],
    display_preferences jsonb not null default '{}'::jsonb,
    
    -- Tracking and metrics
    token_count integer,
    processing_time interval not null,
    cache_hit boolean not null default false,
    created_at timestamp with time zone not null default now(),
    
    -- Constraints
    constraint valid_response_data check (jsonb_typeof(response_data) = 'object'),
    constraint valid_display_preferences check (jsonb_typeof(display_preferences) = 'object')
);

-- Create table for product comparisons
create table if not exists product_comparisons (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    response_id uuid not null references agent_responses(id),
    
    -- Products being compared
    product_a_id uuid not null references products(id),
    product_b_id uuid not null references products(id),
    
    -- Comparison details
    differences jsonb not null,
    focus_areas text[] not null default array[]::text[],
    recommendations text[] not null default array[]::text[],
    
    -- Tracking
    created_at timestamp with time zone not null default now(),
    
    -- Constraints
    constraint different_products check (product_a_id != product_b_id),
    constraint valid_differences check (jsonb_typeof(differences) = 'object')
);

-- Create indexes for performance
create index idx_agent_queries_session on agent_queries(session_id);
create index idx_agent_queries_hash on agent_queries(query_hash);
create index idx_agent_queries_type on agent_queries(query_type);
create index idx_agent_queries_created on agent_queries(created_at);
create index idx_agent_queries_text_trgm on agent_queries using gin (query_text gin_trgm_ops);

create index idx_agent_responses_query on agent_responses(query_id);
create index idx_agent_responses_type on agent_responses(agent_type);
create index idx_agent_responses_created on agent_responses(created_at);
create index idx_agent_responses_cache on agent_responses(cache_hit);

create index idx_product_comparisons_products on product_comparisons(product_a_id, product_b_id);
create index idx_product_comparisons_response on product_comparisons(response_id);

-- Create view for query analytics
create or replace view query_analytics as
select
    q.query_type,
    q.requires_specialist,
    q.specialist_type,
    r.agent_type,
    r.cache_hit,
    avg(q.confidence) as avg_query_confidence,
    avg(r.confidence) as avg_response_confidence,
    avg(extract(epoch from r.processing_time)) as avg_processing_time,
    count(*) as query_count,
    avg(array_length(q.model_numbers, 1)) as avg_products_per_query
from agent_queries q
join agent_responses r on r.query_id = q.id
group by
    q.query_type,
    q.requires_specialist,
    q.specialist_type,
    r.agent_type,
    r.cache_hit;

-- Add RLS policies
alter table agent_queries enable row level security;
alter table agent_responses enable row level security;
alter table product_comparisons enable row level security;

-- Allow read access to authenticated users
create policy "Allow read access to agent queries"
    on agent_queries for select
    to authenticated
    using (true);

create policy "Allow read access to agent responses"
    on agent_responses for select
    to authenticated
    using (true);

create policy "Allow read access to product comparisons"
    on product_comparisons for select
    to authenticated
    using (true);

-- Allow write access only to service role
create policy "Allow write access to agent queries"
    on agent_queries for all
    to service_role
    using (true)
    with check (true);

create policy "Allow write access to agent responses"
    on agent_responses for all
    to service_role
    using (true)
    with check (true);

create policy "Allow write access to product comparisons"
    on product_comparisons for all
    to service_role
    using (true)
    with check (true);

-- Comments for documentation
comment on table agent_queries is 'Tracks all queries received by agents';
comment on table agent_responses is 'Stores agent responses and analysis results';
comment on table product_comparisons is 'Records detailed product comparisons';

-- Revert function for rollback
-- drop view if exists query_analytics;
-- drop table if exists product_comparisons;
-- drop table if exists agent_responses;
-- drop table if exists agent_queries;
-- drop type if exists query_type;
-- drop type if exists agent_type; 