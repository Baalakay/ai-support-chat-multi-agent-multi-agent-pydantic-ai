import { type AIFindings } from '@/types/comparison';

interface AIAnalysisProps {
  findings: AIFindings;
  focus?: {
    section: string;
    category?: string;
    attribute?: string;
  };
}

export function AIAnalysis({ findings, focus }: AIAnalysisProps) {
  if (!findings?.findings?.recommendations?.length) {
    return null;
  }

  const isRelevantContent = (recommendation: typeof findings.findings.recommendations[0]) => {
    if (!focus) return true;

    const contentToCheck = [
      recommendation.model,
      recommendation.context,
      recommendation.category
    ].join(' ').toLowerCase();

    const relevantTerms = [
      focus.section.toLowerCase(),
      focus.category?.toLowerCase(),
      focus.attribute?.toLowerCase()
    ].filter((term): term is string => typeof term === 'string');

    return relevantTerms.some(term => contentToCheck.includes(term));
  };

  // Group recommendations by category
  const groupedRecommendations = findings.findings.recommendations
    .filter(isRelevantContent)
    .reduce((acc, rec) => {
      const category = rec.category || 'General Recommendations';
      if (!acc[category]) acc[category] = [];
      acc[category].push(rec);
      return acc;
    }, {} as Record<string, typeof findings.findings.recommendations>);

  if (Object.keys(groupedRecommendations).length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 text-sm">
      {/* Summary Section */}
      <div className="border-b border-gray-200">
        <div className="bg-blue-50 px-3 py-2">
          <p className="text-blue-900 font-medium">{findings.findings.summary}</p>
        </div>
      </div>

      {/* Recommendations by Category */}
      <div>
        {Object.entries(groupedRecommendations).map(([category, recommendations]) => (
          <div key={category}>
            <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
              <h4 className="font-semibold text-gray-700">{category}</h4>
            </div>
            <ul className="pl-4">
              {recommendations.map((rec, idx) => (
                <li
                  key={`${category}-${idx}`}
                  className={`px-3 py-2 ${focus ? 'bg-yellow-50' : ''} ${
                    idx !== recommendations.length - 1 ? 'border-b border-gray-200' : ''
                  }`}
                >
                  <span className="font-medium text-gray-700">{rec.action}</span>
                  {' '}
                  <span className="font-medium">{rec.model}</span>
                  {' '}
                  <span className="text-gray-700">{rec.context}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Technical Details Section */}
      <div className="border-t border-gray-200">
        <div className="bg-blue-50 px-3 py-2">
          <p className="text-blue-900 font-medium">{findings.findings.technical_details}</p>
        </div>
      </div>
    </div>
  );
} 