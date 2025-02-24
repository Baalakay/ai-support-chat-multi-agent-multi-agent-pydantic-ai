-- Create product documentation table

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create the table
CREATE TABLE product_docs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_number TEXT NOT NULL UNIQUE,
    raw_content JSONB NOT NULL,
    processed_content JSONB NOT NULL,
    metadata JSONB NOT NULL,
    file_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_product_docs_model_number ON product_docs(model_number);
CREATE INDEX idx_product_docs_file_hash ON product_docs(file_hash);
CREATE INDEX idx_product_docs_status ON product_docs(status);
CREATE INDEX idx_product_docs_content ON product_docs USING gin(processed_content jsonb_path_ops);
CREATE INDEX idx_product_docs_raw_text ON product_docs USING gin((raw_content->>'text') gin_trgm_ops);

-- Create function for updating timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updating timestamp
CREATE TRIGGER update_product_docs_updated_at
    BEFORE UPDATE ON product_docs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 