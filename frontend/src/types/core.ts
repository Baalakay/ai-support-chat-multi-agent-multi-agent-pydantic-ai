// Base types for API responses
export interface BaseResult {
  source_file?: string;
  confidence?: number;
}

// Common display settings
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

// Common data structures
export interface DataFrame {
  columns: string[];
  data: Record<string, any>[];
}

// API response wrapper
export interface ApiResponse<T> {
  data: T;
  error?: string;
  metadata?: Record<string, any>;
} 