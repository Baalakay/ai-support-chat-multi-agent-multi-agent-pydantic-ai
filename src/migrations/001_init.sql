BEGIN;

-- Create the pdf_data table
CREATE TABLE IF NOT EXISTS pdf_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_number TEXT NOT NULL,
    data JSONB NOT NULL,
    is_test_data BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (model_number, is_test_data)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pdf_data_model_number ON pdf_data(model_number);
CREATE INDEX IF NOT EXISTS idx_pdf_data_is_test_data ON pdf_data(is_test_data);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update updated_at timestamp
CREATE TRIGGER update_pdf_data_updated_at
    BEFORE UPDATE ON pdf_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create rollback function
CREATE OR REPLACE FUNCTION rollback_000()
RETURNS void AS $$
BEGIN
    DROP TRIGGER IF EXISTS update_pdf_data_updated_at ON pdf_data;
    DROP FUNCTION IF EXISTS update_updated_at_column();
    DROP TABLE IF EXISTS pdf_data;
END;
$$ LANGUAGE plpgsql;

COMMIT; 