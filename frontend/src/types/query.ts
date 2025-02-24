import type { BaseResult, DisplaySections, FocusSettings } from './core';

// Common display and focus settings
export interface SpecificationDisplay {
  show: boolean;
  sections: string[];
}

export interface DisplaySections {
  features: boolean;
  advantages: boolean;
  specifications: SpecificationDisplay;
  differences: SpecificationDisplay;
}

export interface FocusSettings {
  section: string;
  category?: string;
  attribute?: string;
}

// Query analysis and results
export interface QueryAnalysis {
  type: 'single' | 'comparison';
  models: string[];
  specific_attribute?: string | null;
  display_sections: DisplaySections;
  focus?: FocusSettings | null;
  query: string;  // The original user query
}

export interface SingleQueryResult extends BaseResult {
  device?: string;
  specifications: Array<{
    Category: string;
    Specification: string;
    [key: string]: string;
  }>;
  source_file?: string;
  confidence?: number;
} 