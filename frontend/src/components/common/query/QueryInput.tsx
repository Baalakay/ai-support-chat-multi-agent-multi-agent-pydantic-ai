import { useState, type ChangeEvent, type FormEvent } from 'react';
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import { analyzeCombined, analyzeQuery } from '@/services/ai';
import type { QueryAnalysis } from '@/types/query';
import { type VariantProps } from 'class-variance-authority';

interface QueryInputProps {
  onQuery: (analysis: QueryAnalysis) => void;
  disabled?: boolean;
}

type ButtonVariants = VariantProps<typeof buttonVariants>;

const EXAMPLE_QUERIES = [
  "What are the specs of the HSR-520R?",
  "Compare the 520R, 637, and 1016R",
  "Give me the specifications of the 980F",
  "Compare voltage requirements between HSR-980F and HSR-1016",
  "Show differences in magnetic specs for HSR-520, HSR-980, and HSR-1016R"
];

const QUERY_PATTERNS = [
  "Compare [model] and [model]",
  "Show specs for [model]",
  "What are the differences between [model] and [model]",
  "Compare [spec] between [model] and [model]",
  "Show [spec] specs for [model]"
];

const MODEL_NUMBERS = ["HSR-520R", "HSR-980F", "HSR-1016", "HSR-1016R"];
const SPEC_TYPES = ["electrical", "magnetic", "physical", "operational"];

export function QueryInput({ onQuery, disabled }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingState, setLoadingState] = useState<'idle' | 'analyzing' | 'processing'>('idle');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleExampleClick = (example: string) => {
    setQuery(example);
    setShowSuggestions(false);
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setLoadingState('analyzing');
    setShowSuggestions(false);

    try {
      // Get the query analysis
      const queryAnalysis = await analyzeQuery(query);
      console.log('Query analysis:', queryAnalysis);
      
      // Add the original query to the analysis
      const analysisWithQuery = {
        ...queryAnalysis,
        query: query.trim()
      };
      
      // Pass the query analysis directly to the parent
      setLoadingState('processing');
      onQuery(analysisWithQuery);
    } catch (err) {
      console.error('Error analyzing query:', err);
      setError(err instanceof Error ? err.message : 'Failed to analyze query');
    } finally {
      setLoading(false);
      setLoadingState('idle');
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    if (error) setError(null);

    // Generate suggestions based on input
    if (value.trim()) {
      const suggestions = QUERY_PATTERNS.map(pattern => {
        let suggestion = pattern;
        if (value.toLowerCase().includes('compare')) {
          suggestion = suggestion.replace(/\[model\]/g, () => MODEL_NUMBERS[Math.floor(Math.random() * MODEL_NUMBERS.length)]);
          suggestion = suggestion.replace(/\[spec\]/g, () => SPEC_TYPES[Math.floor(Math.random() * SPEC_TYPES.length)]);
        }
        return suggestion;
      });
      setSuggestions(suggestions);
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleFocus = () => {
    if (query.trim()) {
      setShowSuggestions(true);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
  };

  const getLoadingText = () => {
    switch (loadingState) {
      case 'analyzing':
        return 'Analyzing query...';
      case 'processing':
        return 'Processing results...';
      default:
        return 'Ask Herm';
    }
  };

  const getButtonVariant = (): ButtonVariants['variant'] => {
    if (loading) return 'outline';
    if (error) return 'destructive';
    return 'default';
  };

  return (
    <div className="space-y-4 p-4 bg-white rounded-lg shadow-sm border border-[#e0e0e0]">
      <div className="relative">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder="Ask about specific features or compare models..."
              value={query}
              onChange={handleChange}
              onFocus={handleFocus}
              className={`flex-1 text-[16px] ${loading ? 'bg-[#f8f9fa]' : ''}`}
              disabled={disabled || loading}
              aria-label="Query input"
              aria-invalid={error ? 'true' : 'false'}
              aria-describedby={error ? 'query-error' : undefined}
              list="query-suggestions"
            />
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-[#e0e0e0] rounded-md shadow-lg">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-[#f8f9fa] focus:bg-[#f8f9fa] focus:outline-none"
                    onClick={() => handleSuggestionClick(suggestion)}
                    type="button"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
          <Button 
            type="submit" 
            disabled={disabled || loading}
            aria-busy={loading}
            variant={getButtonVariant()}
            className="min-w-[120px] relative font-medium"
          >
            {loading && (
              <span className="absolute inset-0 flex items-center justify-center bg-opacity-50">
                <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
            )}
            <span className={loading ? 'opacity-0' : ''}>
              {getLoadingText()}
            </span>
          </Button>
        </form>
      </div>

      {error && (
        <p className="text-sm text-red-600 font-medium" role="alert" id="query-error">
          {error}
        </p>
      )}
      
      {loading && (
        <p className="text-sm text-[#1a1a1a] opacity-75" role="status">
          {loadingState === 'analyzing' ? 
            'Analyzing your query and identifying relevant model features...' :
            'Processing comparison results and generating insights...'}
        </p>
      )}

      {/* Example Queries */}
      <div className="pt-3 border-t border-[#e0e0e0]">
        <p className="text-sm font-medium text-[#1a1a1a] mb-2">Try these examples:</p>
        <div className="space-y-2">
          {EXAMPLE_QUERIES.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              className="block w-full text-left text-sm text-[#1a73e8] hover:text-[#1557b0] hover:bg-[#f8f9fa] px-2 py-1 rounded transition-colors"
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
} 