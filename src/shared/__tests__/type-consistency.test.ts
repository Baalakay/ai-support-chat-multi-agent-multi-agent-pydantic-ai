/**
 * Tests to verify type consistency between frontend and backend interfaces
 */

import { z } from 'zod';
import {
  productQuerySchema,
  productResponseSchema,
  technicalSpecsSchema,
  apiErrorSchema,
  validationErrorSchema
} from '../schemas';

describe('API Error Schema Consistency', () => {
  it('validates correct error format', () => {
    const validError = {
      detail: 'Invalid request',
      status_code: 400,
      timestamp: new Date().toISOString(),
      validation_errors: [{
        loc: ['body', 'model_numbers', 0],
        msg: 'Invalid model number',
        type: 'value_error'
      }],
      metadata: {
        request_id: '123'
      }
    };

    expect(() => apiErrorSchema.parse(validError)).not.toThrow();
  });

  it('requires all mandatory error fields', () => {
    const invalidError = {
      detail: 'Invalid request',
      // missing status_code
      timestamp: new Date().toISOString()
    };

    expect(() => apiErrorSchema.parse(invalidError)).toThrow();
  });

  it('validates validation error format', () => {
    const validValidationError = {
      loc: ['body', 'field', 0],
      msg: 'Error message',
      type: 'error_type'
    };

    expect(() => validationErrorSchema.parse(validValidationError)).not.toThrow();
  });
});

describe('Product Query Schema Consistency', () => {
  it('validates correct query format', () => {
    const validQuery = {
      model_numbers: ['ABC123', 'XYZ789'],
      focus_areas: [{
        section: 'technical',
        category: 'electrical',
        specification: 'voltage'
      }],
      display_preferences: {
        sectionsToShow: ['technical', 'mechanical'],
        comparisonMode: 'full' as const,
        showDifferencesOnly: false,
        layout: 'stacked' as const
      }
    };

    expect(() => productQuerySchema.parse(validQuery)).not.toThrow();
  });

  it('requires model numbers', () => {
    const invalidQuery = {
      // missing model_numbers
      focus_areas: []
    };

    expect(() => productQuerySchema.parse(invalidQuery)).toThrow();
  });
});

describe('Product Response Schema Consistency', () => {
  it('validates correct response format', () => {
    const validResponse = {
      customer_support: {
        queryType: 'single' as const,
        modelNumbers: ['ABC123'],
        focusAreas: [{
          section: 'technical'
        }],
        displayPreferences: {
          sectionsToShow: ['technical'],
          comparisonMode: 'full' as const,
          showDifferencesOnly: false,
          layout: 'stacked' as const
        },
        metadata: {}
      },
      product_specialist: {
        technicalAnalysis: {
          details: {
            technical: [{
              section: 'technical',
              category: 'electrical',
              specification: 'voltage',
              analysis: 'Analysis text',
              importance: 'high' as const
            }]
          },
          summary: 'Summary text',
          keyPoints: ['Point 1'],
          bestUses: ['Use 1'],
          considerations: ['Consideration 1'],
          confidence: 0.95
        },
        metadata: {}
      },
      metadata: {}
    };

    expect(() => productResponseSchema.parse(validResponse)).not.toThrow();
  });
});

describe('Technical Specs Schema Consistency', () => {
  it('validates correct specs format', () => {
    const validSpecs = {
      sections: {
        technical: {
          categories: {
            electrical: {
              specs: {
                voltage: {
                  value: '24V',
                  unit: 'V',
                  description: 'Operating voltage'
                }
              },
              description: 'Electrical specifications'
            }
          },
          description: 'Technical specifications'
        }
      },
      metadata: {}
    };

    expect(() => technicalSpecsSchema.parse(validSpecs)).not.toThrow();
  });

  it('validates nested structure requirements', () => {
    const invalidSpecs = {
      sections: {
        technical: {
          // missing categories
          description: 'Technical specifications'
        }
      },
      metadata: {}
    };

    expect(() => technicalSpecsSchema.parse(invalidSpecs)).toThrow();
  });
}); 