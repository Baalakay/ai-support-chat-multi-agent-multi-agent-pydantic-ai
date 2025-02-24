/**
 * Tests to verify schema compatibility between Zod and Pydantic
 */

import { z } from 'zod';
import {
  productQuerySchema,
  productResponseSchema,
  technicalSpecsSchema,
  apiErrorSchema,
  validationErrorSchema,
  type ProductQuery,
  type ProductResponse,
  type TechnicalSpecs,
  type APIError,
  type ValidationError
} from '../schemas';

// Helper to ensure types are assignable
const assertType = <T>(_value: T) => {};

describe('Schema Type Compatibility', () => {
  it('validates ProductQuery type compatibility', () => {
    const query: ProductQuery = {
      model_numbers: ['ABC123'],
      focus_areas: [{
        section: 'technical',
        category: 'electrical'
      }],
      display_preferences: {
        sectionsToShow: ['technical'],
        comparisonMode: 'full',
        showDifferencesOnly: false,
        layout: 'stacked'
      }
    };

    // Should satisfy both Zod schema and TypeScript type
    assertType<ProductQuery>(query);
    expect(() => productQuerySchema.parse(query)).not.toThrow();
  });

  it('validates ProductResponse type compatibility', () => {
    const response: ProductResponse = {
      customer_support: {
        queryType: 'single',
        modelNumbers: ['ABC123'],
        focusAreas: [],
        displayPreferences: {
          sectionsToShow: [],
          comparisonMode: 'full',
          showDifferencesOnly: false,
          layout: 'stacked'
        },
        metadata: {}
      },
      product_specialist: {
        technicalAnalysis: {
          details: {},
          summary: '',
          keyPoints: [],
          bestUses: [],
          considerations: [],
          confidence: 1
        },
        metadata: {}
      },
      metadata: {}
    };

    // Should satisfy both Zod schema and TypeScript type
    assertType<ProductResponse>(response);
    expect(() => productResponseSchema.parse(response)).not.toThrow();
  });

  it('validates TechnicalSpecs type compatibility', () => {
    const specs: TechnicalSpecs = {
      sections: {},
      metadata: {}
    };

    // Should satisfy both Zod schema and TypeScript type
    assertType<TechnicalSpecs>(specs);
    expect(() => technicalSpecsSchema.parse(specs)).not.toThrow();
  });

  it('validates APIError type compatibility', () => {
    const error: APIError = {
      detail: 'Error',
      status_code: 400,
      timestamp: new Date().toISOString(),
      validation_errors: [{
        loc: ['test'],
        msg: 'Test',
        type: 'error'
      }],
      metadata: {}
    };

    // Should satisfy both Zod schema and TypeScript type
    assertType<APIError>(error);
    expect(() => apiErrorSchema.parse(error)).not.toThrow();
  });

  it('validates ValidationError type compatibility', () => {
    const error: ValidationError = {
      loc: ['test'],
      msg: 'Test',
      type: 'error'
    };

    // Should satisfy both Zod schema and TypeScript type
    assertType<ValidationError>(error);
    expect(() => validationErrorSchema.parse(error)).not.toThrow();
  });
});

describe('Schema Inference Compatibility', () => {
  it('validates Zod inference matches TypeScript types', () => {
    type InferredProductQuery = z.infer<typeof productQuerySchema>;
    type InferredProductResponse = z.infer<typeof productResponseSchema>;
    type InferredTechnicalSpecs = z.infer<typeof technicalSpecsSchema>;
    type InferredAPIError = z.infer<typeof apiErrorSchema>;
    type InferredValidationError = z.infer<typeof validationErrorSchema>;

    // These type assertions will fail if inferred types don't match
    assertType<InferredProductQuery>({} as ProductQuery);
    assertType<InferredProductResponse>({} as ProductResponse);
    assertType<InferredTechnicalSpecs>({} as TechnicalSpecs);
    assertType<InferredAPIError>({} as APIError);
    assertType<InferredValidationError>({} as ValidationError);
  });
}); 