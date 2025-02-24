-- Create analytics and caching tables
-- Migration: 20240101000003_create_analytics_tables

-- Create table for response caching
create table if not exists response_cache (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    cache_key text not null unique,
    context_hash text,
    
    -- Cached data
    response_data jsonb not null,
    agent_type agent_type not null,
    
    -- Cache management
    created_at timestamp with time zone not null default now(),
    expires_at timestamp with time zone not null,
    hit_count integer not null default 0,
    last_accessed timestamp with time zone,
    
    -- Constraints
    constraint valid_response_data check (jsonb_typeof(response_data) = 'object'),
    constraint valid_expiry check (expires_at > created_at)
);

-- Create table for usage tracking
create table if not exists agent_usage (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    session_id uuid not null,
    agent_type agent_type not null,
    
    -- Usage metrics
    prompt_tokens integer not null default 0,
    completion_tokens integer not null default 0,
    total_tokens integer not null default 0,
    request_count integer not null default 0,
    cache_hits integer not null default 0,
    
    -- Time tracking
    total_processing_time interval not null default interval '0',
    first_request timestamp with time zone not null default now(),
    last_request timestamp with time zone not null default now(),
    
    -- Cost tracking (in USD)
    prompt_cost numeric(10,6) not null default 0,
    completion_cost numeric(10,6) not null default 0,
    total_cost numeric(10,6) not null default 0,
    
    -- Constraints
    constraint valid_tokens check (
        prompt_tokens >= 0 and
        completion_tokens >= 0 and
        total_tokens = prompt_tokens + completion_tokens
    ),
    constraint valid_costs check (
        prompt_cost >= 0 and
        completion_cost >= 0 and
        total_cost = prompt_cost + completion_cost
    )
);

-- Create table for performance metrics
create table if not exists performance_metrics (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    agent_type agent_type not null,
    metric_type text not null,
    
    -- Time window
    window_start timestamp with time zone not null,
    window_end timestamp with time zone not null,
    window_size interval not null,
    
    -- Metrics
    request_count integer not null default 0,
    error_count integer not null default 0,
    cache_hit_rate numeric(5,2) not null default 0,
    avg_response_time interval not null,
    p95_response_time interval not null,
    avg_token_count integer not null default 0,
    total_cost numeric(10,6) not null default 0,
    
    -- Constraints
    constraint valid_window check (window_end > window_start),
    constraint valid_rates check (cache_hit_rate between 0 and 100)
);

-- Create indexes for performance
create index idx_response_cache_key on response_cache(cache_key);
create index idx_response_cache_context on response_cache(context_hash) where context_hash is not null;
create index idx_response_cache_expiry on response_cache(expires_at);
create index idx_response_cache_accessed on response_cache(last_accessed);

create index idx_agent_usage_session on agent_usage(session_id);
create index idx_agent_usage_type on agent_usage(agent_type);
create index idx_agent_usage_requests on agent_usage(last_request);

create index idx_performance_metrics_window on performance_metrics(window_start, window_end);
create index idx_performance_metrics_type on performance_metrics(agent_type, metric_type);

-- Create function to update cache hit count
create or replace function update_cache_hit()
returns trigger as $$
begin
    new.hit_count = new.hit_count + 1;
    new.last_accessed = now();
    return new;
end;
$$ language plpgsql;

-- Create trigger for cache hits
create trigger cache_hit_counter
    before update on response_cache
    for each row
    when (old.hit_count is distinct from new.hit_count)
    execute function update_cache_hit();

-- Create view for agent performance summary
create or replace view agent_performance_summary as
select
    agent_type,
    date_trunc('hour', window_start) as time_bucket,
    sum(request_count) as total_requests,
    avg(cache_hit_rate) as avg_cache_hit_rate,
    avg(extract(epoch from avg_response_time)) as avg_response_time_seconds,
    sum(total_cost) as total_cost,
    sum(error_count)::float / nullif(sum(request_count), 0) * 100 as error_rate
from performance_metrics
group by
    agent_type,
    date_trunc('hour', window_start)
order by
    agent_type,
    time_bucket;

-- Add RLS policies
alter table response_cache enable row level security;
alter table agent_usage enable row level security;
alter table performance_metrics enable row level security;

-- Allow read access to authenticated users
create policy "Allow read access to response cache"
    on response_cache for select
    to authenticated
    using (true);

create policy "Allow read access to agent usage"
    on agent_usage for select
    to authenticated
    using (true);

create policy "Allow read access to performance metrics"
    on performance_metrics for select
    to authenticated
    using (true);

-- Allow write access only to service role
create policy "Allow write access to response cache"
    on response_cache for all
    to service_role
    using (true)
    with check (true);

create policy "Allow write access to agent usage"
    on agent_usage for all
    to service_role
    using (true)
    with check (true);

create policy "Allow write access to performance metrics"
    on performance_metrics for all
    to service_role
    using (true)
    with check (true);

-- Comments for documentation
comment on table response_cache is 'Caches agent responses for performance optimization';
comment on table agent_usage is 'Tracks token usage and costs per agent session';
comment on table performance_metrics is 'Stores aggregated performance metrics';

-- Revert function for rollback
-- drop view if exists agent_performance_summary;
-- drop trigger if exists cache_hit_counter on response_cache;
-- drop function if exists update_cache_hit;
-- drop table if exists performance_metrics;
-- drop table if exists agent_usage;
-- drop table if exists response_cache; 