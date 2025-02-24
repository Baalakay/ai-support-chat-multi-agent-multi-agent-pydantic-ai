import { useState } from 'react'
import type { ComparisonResult } from './types/comparison'
import type { SingleQueryResult, QueryAnalysis } from './types/query'
import { api } from './services/api'
import { SpecificationTable } from './components/common/results/SpecificationTable'
import { FeatureAdvantageTable } from './components/common/results/FeatureAdvantageTable'
import { SingleSpecificationTable } from './components/common/results/SingleSpecificationTable'
import { AIAnalysis } from './components/common/query/AIAnalysis'
import { QueryInput } from './components/common/query/QueryInput'
import { Accordion } from './components/ui/Accordion'
import { ChatbotIcon } from './components/icons/ChatbotIcon'
import { ErrorBoundary } from './components/ErrorBoundary'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AdminPage } from './pages/Admin'

function App() {
  const [comparisonData, setComparisonData] = useState<ComparisonResult | null>(null)
  const [singleQueryData, setSingleQueryData] = useState<SingleQueryResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentQuery, setCurrentQuery] = useState<QueryAnalysis | null>(null)

  const handleQuery = async (analysis: QueryAnalysis) => {
    setLoading(true)
    setError(null)
    setCurrentQuery(analysis)
    setSingleQueryData(null)
    setComparisonData(null)

    try {
      if (analysis.type === 'comparison' && analysis.models.length > 1) {
        const result = await api.compare(analysis.models)
        console.log('Comparison result:', result)
        if (!result.spec_differences_df) {
          result.spec_differences_df = result.specs_df
        }
        console.log('AI Findings:', result.findings)
        setComparisonData(result)
      } else {
        // For single queries, send the original query
        const data = await api.chat(analysis.query)
        setSingleQueryData(data)
      }
    } catch (err) {
      console.error('Error in handleQuery:', err)
      setError(err instanceof Error ? err.message : 'Failed to process request')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Link to="/" className="text-xl font-bold text-gray-900">
                    PDF RAG Chatbot
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                  >
                    Query
                  </Link>
                  <Link
                    to="/admin"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900"
                  >
                    Admin
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main>
          <Routes>
            <Route path="/" element={
              <ErrorBoundary>
                <div className="min-h-screen bg-gray-50">
                  <div className="container mx-auto pr-4 py-8">
                    <div className="flex items-center gap-4 mb-8 pl-4">
                      <div className="relative">
                        <ChatbotIcon className="w-16 h-16 fill-current" />
                      </div>
                      <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
                          Hi, I'm Herm!
                        </h1>
                        <p className="text-lg text-gray-600">
                          The HSI AI Assistant! Ask me anything about our products.
                        </p>
                      </div>
                    </div>
                    
                    {/* Query Input */}
                    <div className="mb-8 px-4">
                      <QueryInput
                        onQuery={handleQuery}
                        disabled={loading}
                      />
                    </div>

                    {loading && (
                      <div className="text-center py-8 px-4">
                        <p>Processing your request...</p>
                      </div>
                    )}

                    {error && (
                      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mx-4">
                        {error}
                      </div>
                    )}

                    {comparisonData && currentQuery?.type === 'comparison' && currentQuery.display_sections && (
                      <div>
                        <div className="space-y-4">
                          {/* Features and Advantages Section */}
                          {(currentQuery.display_sections.features || currentQuery.display_sections.advantages) && (
                            <div className="px-4">
                              <FeatureAdvantageTable 
                                featuresData={comparisonData.features_df}
                                advantagesData={comparisonData.advantages_df}
                              />
                            </div>
                          )}
                        </div>

                        {/* Specifications Section */}
                        {currentQuery.display_sections.specifications?.show && (
                          <div className="mt-4 px-4">
                            <SpecificationTable
                              data={comparisonData.specs_df}
                              type={currentQuery.type}
                              highlightDifferences={currentQuery.display_sections.specifications?.highlight_differences}
                              sections={currentQuery.display_sections.specifications?.sections}
                              focus={currentQuery.display_sections.specifications?.focus}
                            />
                          </div>
                        )}

                        <div className="space-y-4 mt-4">
                          {/* Differences Section */}
                          {currentQuery.display_sections.specifications?.show && comparisonData.spec_differences_df && (
                            <div className="px-4">
                              <SpecificationTable 
                                data={comparisonData.spec_differences_df}
                                type="differences"
                                sections={currentQuery.display_sections.specifications.sections}
                                focus={currentQuery.focus}
                                highlightDifferences={false}
                                showModelHeaders={false}
                                title="Differences"
                              />
                            </div>
                          )}

                          {/* AI Analysis Section */}
                          {comparisonData?.findings && (
                            <div className="px-4">
                              <div className="min-w-[900px] border border-gray-200 rounded-md shadow-sm">
                                <Accordion title="Herms AI Recommendations" defaultOpen={true} className="p-0 [&>button]:text-left [&>button]:bg-[#f7941c] [&>button]:text-white [&>button]:hover:bg-[#f7941c]/90">
                                  <div>
                                    <AIAnalysis findings={comparisonData.findings} focus={currentQuery.focus} />
                                  </div>
                                </Accordion>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Single Query Response */}
                    {singleQueryData && currentQuery?.type === 'single' && (
                      <div className="px-4">
                        <div>
                          <SpecificationTable 
                            data={{
                              columns: ['Category', 'Specification', singleQueryData.device || 'Device'],
                              data: singleQueryData.specifications
                            }}
                            type="specifications"
                          />
                          {(singleQueryData.source_file || singleQueryData.confidence) && (
                            <div className="p-4 bg-gray-50 border-t border-gray-200 text-sm mt-[-1px]">
                              {singleQueryData.source_file && (
                                <div className="text-gray-600">
                                  Source: {singleQueryData.source_file}
                                </div>
                              )}
                              {singleQueryData.confidence && (
                                <div className="text-gray-600 mt-1">
                                  Confidence: {(singleQueryData.confidence * 100).toFixed(1)}%
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </ErrorBoundary>
            } />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App
