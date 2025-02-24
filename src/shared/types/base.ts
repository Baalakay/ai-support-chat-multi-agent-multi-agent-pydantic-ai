/**
 * Base types shared between frontend and backend
 */

export type Importance = 'critical' | 'high' | 'medium' | 'low';
export type ComparisonMode = 'full' | 'differences';
export type QueryType = 'single' | 'multi' | 'specific';
export type LayoutMode = 'stacked' | 'sideBySide';

export interface Metadata {
  sourceFile?: string;
  confidence?: number;
  timestamp?: string;
  [key: string]: unknown;
}

export interface BaseResponse {
  success: boolean;
  error?: string;
  metadata?: Metadata;
} 