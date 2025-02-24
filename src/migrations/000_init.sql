-- Setup migration function
BEGIN;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create PDF data table
CREATE TABLE IF NOT EXISTS public.pdf_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_number TEXT NOT NULL,
    data JSONB NOT NULL,
    is_test_data BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_model_number CHECK (model_number ~ '^[0-9]+[RFW]?$'),
    UNIQUE (model_number, is_test_data)
);

-- Create basic indexes
CREATE INDEX IF NOT EXISTS idx_pdf_data_model_number ON public.pdf_data(model_number);
CREATE INDEX IF NOT EXISTS idx_pdf_data_is_test_data ON public.pdf_data(is_test_data);

-- Add function to update timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS pdf_data_updated_at ON public.pdf_data;
CREATE TRIGGER pdf_data_updated_at
    BEFORE UPDATE ON public.pdf_data
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();

-- Grant permissions
GRANT ALL ON public.pdf_data TO authenticated;
GRANT ALL ON public.pdf_data TO service_role;

-- Rollback function
CREATE OR REPLACE FUNCTION public.rollback_000()
RETURNS void AS $$
BEGIN
    DROP TABLE IF EXISTS public.pdf_data;
    DROP FUNCTION IF EXISTS public.update_updated_at();
END;
$$ LANGUAGE plpgsql;

COMMIT; 