/**
 * Zod schemas for base types
 */

import { z } from 'zod';
import type * as Types from '../types/base';

export const importanceSchema = z.enum(['critical', 'high', 'medium', 'low']);
export const comparisonModeSchema = z.enum(['full', 'differences']);
export const queryTypeSchema = z.enum(['single', 'multi', 'specific']);
export const layoutModeSchema = z.enum(['stacked', 'sideBySide']);

export const metadataSchema = z.object({
  sourceFile: z.string().optional(),
  confidence: z.number().optional(),
  timestamp: z.string().optional(),
}).catchall(z.unknown());

export const baseResponseSchema = z.object({
  success: z.boolean(),
  error: z.string().optional(),
  metadata: metadataSchema.optional(),
});

// Type validation helpers
export const validateImportance = (value: unknown): Types.Importance => importanceSchema.parse(value);
export const validateComparisonMode = (value: unknown): Types.ComparisonMode => comparisonModeSchema.parse(value);
export const validateQueryType = (value: unknown): Types.QueryType => queryTypeSchema.parse(value);
export const validateLayoutMode = (value: unknown): Types.LayoutMode => layoutModeSchema.parse(value);
export const validateMetadata = (value: unknown): Types.Metadata => metadataSchema.parse(value);
export const validateBaseResponse = (value: unknown): Types.BaseResponse => baseResponseSchema.parse(value); 