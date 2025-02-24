import { type DataFrame } from '@/types/core';
import { Accordion } from "../../ui/Accordion";

interface FeatureAdvantageTableProps {
  featuresData: DataFrame;
  advantagesData: DataFrame;
}

export function FeatureAdvantageTable({ featuresData, advantagesData }: FeatureAdvantageTableProps) {
  const modelColumns = featuresData.columns.filter(col => col !== '');
  
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: '300px minmax(0px, 1fr) repeat(3, 180px)',
    alignItems: 'center',
    width: '100%'
  };

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[900px] border border-gray-200 rounded-md shadow-sm">
        <Accordion 
          title={
            <h3 className="font-medium text-white text-left pl-4">Features and Advantages</h3>
          }
          defaultOpen={true}
          className="border-0 shadow-none rounded-none [&>button]:bg-[#f7941c] [&>button]:text-white [&>button]:hover:bg-[#f7941c]/90"
        >
          <div className="border-t border-gray-200">
            {/* Features Section */}
            <div className="bg-gray-50 border-b border-gray-200">
              <div style={gridStyle}>
                <div className="px-12 py-0.5 font-semibold text-sm">Features</div>
                <div></div>
                {modelColumns.map((model, idx) => (
                  <div key={idx} className="text-sm text-center">{model}</div>
                ))}
              </div>
            </div>
            {featuresData.data.map((row, idx) => {
              const isLastFeature = idx === featuresData.data.length - 1;
              return (
                <div 
                  key={`feature-${idx}`}
                  className={`text-sm ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  } ${!isLastFeature ? 'border-b' : ''} border-gray-200`}
                  style={gridStyle}
                >
                  <div className="px-12 py-0.5 whitespace-nowrap">
                    {row['']}
                  </div>
                  <div></div>
                  {modelColumns.map((model) => (
                    <div 
                      key={model}
                      className="text-center"
                    >
                      {row[model] === '✓' ? (
                        <span className="text-green-600">✓</span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </div>
                  ))}
                </div>
              );
            })}

            {/* Advantages Section */}
            <div className="bg-gray-50 border-b border-gray-200">
              <div style={gridStyle}>
                <div className="px-12 py-0.5 font-semibold text-sm">Advantages</div>
                <div></div>
                {modelColumns.map((model, idx) => (
                  <div key={idx} className="text-sm text-center">{model}</div>
                ))}
              </div>
            </div>
            {advantagesData.data.map((row, idx) => {
              const isLastAdvantage = idx === advantagesData.data.length - 1;
              return (
                <div 
                  key={`advantage-${idx}`}
                  className={`text-sm ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  } ${!isLastAdvantage ? 'border-b' : ''} border-gray-200`}
                  style={gridStyle}
                >
                  <div className="px-12 py-0.5 whitespace-nowrap">
                    {row['']}
                  </div>
                  <div></div>
                  {modelColumns.map((model) => (
                    <div 
                      key={model}
                      className="text-center"
                    >
                      {row[model] === '✓' ? (
                        <span className="text-green-600">✓</span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </Accordion>
      </div>
    </div>
  );
} 