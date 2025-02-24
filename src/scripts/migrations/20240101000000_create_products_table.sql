-- Create products table for storing technical specifications
-- Migration: 20240101000000_create_products_table

-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create enum for product categories
create type product_category as enum (
    'electrical',
    'mechanical',
    'software',
    'system'
);

-- Create products table
create table if not exists products (
    -- Primary key and identification
    id uuid primary key default uuid_generate_v4(),
    model_number text not null unique,
    
    -- Technical specifications stored as JSONB for flexibility
    specifications jsonb not null default '{}'::jsonb,
    features text[] not null default array[]::text[],
    
    -- Metadata and timestamps
    category product_category not null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamp with time zone not null default now(),
    last_updated timestamp with time zone not null default now(),
    
    -- Validation constraints
    constraint valid_model_number check (length(model_number) > 0),
    constraint valid_specifications check (jsonb_typeof(specifications) = 'object'),
    constraint valid_metadata check (jsonb_typeof(metadata) = 'object')
);

-- Create indexes for performance
create index idx_products_model_number on products (model_number);
create index idx_products_category on products (category);
create index idx_products_last_updated on products (last_updated);
create index idx_products_specs_gin on products using gin (specifications jsonb_path_ops);

-- Create function to update last_updated timestamp
create or replace function update_last_updated()
returns trigger as $$
begin
    new.last_updated = now();
    return new;
end;
$$ language plpgsql;

-- Create trigger to automatically update last_updated
create trigger products_last_updated
    before update on products
    for each row
    execute function update_last_updated();

-- Create view for product summaries
create or replace view product_summaries as
select
    id,
    model_number,
    category,
    array_length(features, 1) as feature_count,
    jsonb_object_keys(specifications) as spec_categories,
    last_updated
from products;

-- Add RLS policies
alter table products enable row level security;

-- Allow read access to all authenticated users
create policy "Allow read access to all authenticated users"
    on products for select
    to authenticated
    using (true);

-- Allow write access only to service role
create policy "Allow write access only to service role"
    on products for all
    to service_role
    using (true)
    with check (true);

-- Comments for documentation
comment on table products is 'Product technical specifications and features';
comment on column products.model_number is 'Unique product model number';
comment on column products.specifications is 'Technical specifications stored as JSONB';
comment on column products.features is 'Array of product features';
comment on column products.category is 'Product category (electrical, mechanical, etc.)';
comment on column products.metadata is 'Additional metadata stored as JSONB';

-- Revert function for rollback
-- drop trigger if exists products_last_updated on products;
-- drop function if exists update_last_updated;
-- drop view if exists product_summaries;
-- drop table if exists products;
-- drop type if exists product_category; 