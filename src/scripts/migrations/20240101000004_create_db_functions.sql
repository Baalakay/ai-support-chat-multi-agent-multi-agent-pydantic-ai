-- Create database functions for agent operations
-- Migration: 20240101000004_create_db_functions

-- Function to get product data
create or replace function get_product_data(
    p_model_number text
)
returns table (
    model_number text,
    data jsonb
) as $$
begin
    return query
    select
        p.model_number,
        p.data
    from products p
    where p.model_number = p_model_number;
end;
$$ language plpgsql;

-- Function to store product data
create or replace function store_product_data(
    p_model_number text,
    p_data jsonb
)
returns void as $$
begin
    insert into products (model_number, data)
    values (p_model_number, p_data)
    on conflict (model_number) do update
    set data = p_data;
end;
$$ language plpgsql;

-- Function to search products
create or replace function search_products(
    p_query text,
    p_limit integer default 10
)
returns table (
    model_number text,
    data jsonb,
    rank float4
) as $$
begin
    return query
    select
        p.model_number,
        p.data,
        ts_rank_cd(
            to_tsvector('english', p.data->>'name' || ' ' || p.data->>'description'),
            plainto_tsquery('english', p_query)
        ) as rank
    from products p
    where
        to_tsvector('english', p.data->>'name' || ' ' || p.data->>'description')
        @@ plainto_tsquery('english', p_query)
    order by rank desc
    limit p_limit;
end;
$$ language plpgsql;

-- Function to get technical specifications
create or replace function get_technical_specs(
    p_model_number text
)
returns table (
    model_number text,
    technical_specs jsonb
) as $$
begin
    return query
    select
        ps.model_number,
        ps.technical_specs
    from product_specifications ps
    where ps.model_number = p_model_number;
end;
$$ language plpgsql;

-- Comments for documentation
comment on function get_product_data(text) is 'Get product data by model number';
comment on function store_product_data(text, jsonb) is 'Store or update product data';
comment on function search_products(text, integer) is 'Search products by text query';
comment on function get_technical_specs(text) is 'Get technical specifications by model number';

-- Revert function for rollback
-- drop function if exists get_product_data(text);
-- drop function if exists store_product_data(text, jsonb);
-- drop function if exists search_products(text, integer);
-- drop function if exists get_technical_specs(text); 