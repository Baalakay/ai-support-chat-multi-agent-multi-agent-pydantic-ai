import type { QueryAnalysis } from './query';
import type { BaseResult, DataFrame } from './core';

// Types matching backend output structures
export interface SpecValue {
  unit?: string;
  value: string | number;
}

export interface CategorySpec {
  subcategories: Record<string, SpecValue>;
}

export interface SectionData {
  categories: Record<string, CategorySpec>;
}

export interface PDFData {
  model_name: string;  // Full model name (e.g., "HSR-520R")
  sections: Record<string, SectionData>;
  notes?: Record<string, string>;
  diagram_path?: string;
}

export interface Recommendation {
  action: string;
  model: string;
  context: string;
  category: string;
}

export interface StructuredFindings {
  recommendations: Recommendation[];
  summary: string;
  technical_details: string;
}

export interface AIFindings {
  findings: StructuredFindings;
}

export interface CombinedAnalysis {
  query_analysis: QueryAnalysis;
  findings: AIFindings;
}

export interface ComparisonResult extends BaseResult {
  features_df: DataFrame;
  advantages_df: DataFrame;
  specs_df: DataFrame;
  spec_differences_df: DataFrame;
  findings?: AIFindings;
} 