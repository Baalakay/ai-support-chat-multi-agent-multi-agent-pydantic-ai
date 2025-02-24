import type { QueryAnalysis } from '@/types/query';
import type { CombinedAnalysis } from '@/types/comparison';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

console.log('API Base URL:', API_BASE_URL);

export async function analyzeQuery(query: string): Promise<QueryAnalysis> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error analyzing query:', error);
    // Return default analysis
    return {
      type: 'single',
      models: [],
      displaySections: {
        features: true,
        advantages: true,
        specifications: {
          show: true,
          sections: [],
        },
        differences: {
          show: false,
          sections: [],
        },
      },
    };
  }
}

export async function analyzeCombined(
  query: string,
  modelNames: string[],
  differences: Record<string, Record<string, string>>
): Promise<CombinedAnalysis> {
  try {
    console.log('Making combined analysis request:', {
      query,
      model_names: modelNames,  // Using snake_case to match backend
      differences,
    });

    const response = await fetch(`${API_BASE_URL}/api/analysis/combined`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        query,
        model_names: modelNames,
        differences,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Combined analysis response:', result);
    return result;
  } catch (error) {
    console.error('Error in combined analysis:', error);
    throw error;
  }
} 