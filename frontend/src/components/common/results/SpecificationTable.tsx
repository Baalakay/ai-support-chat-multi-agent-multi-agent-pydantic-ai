import { type DataFrame } from '@/types/core';
import { useMemo, Fragment } from 'react';
import { DiagramThumbnail } from "./DiagramThumbnail";
import { Accordion } from "../../ui/Accordion";

interface DataRow {
  Category: string;
  Specification: string;
  [key: string]: string | null;  // Model values are strings or null
}

interface SpecificationTableProps {
  data: DataFrame;
  type: 'specifications' | 'differences';
  highlightDifferences?: boolean;
  sections?: string[];
  focus?: {
    section: string;
    category?: string;
    attribute?: string;
  };
  title?: string;
}

export function SpecificationTable({ 
  data, 
  type, 
  highlightDifferences = false,
  sections,
  focus,
  title = "Technical Specifications"
}: SpecificationTableProps) {
  // Get model columns (excluding Category and Specification)
  const modelColumns = useMemo(() => {
    return data.columns.filter((col: string) => col !== 'Category' && col !== 'Specification');
  }, [data.columns]);

  // Helper function to determine section based on category
  function determineSection(category: string): string {
    const electricalCategories = ['Power', 'Voltage', 'Current', 'Resistance', 'Capacitance'];
    const magneticCategories = ['Pull - In Range', 'Test Coil'];
    
    if (electricalCategories.includes(category)) {
      return 'Electrical Specifications';
    } else if (magneticCategories.includes(category)) {
      return 'Magnetic Specifications';
    }
    return 'Physical/Operational Specifications';
  }

  // Group data by section and category
  const groupedData = useMemo(() => {
    const groups: Record<string, Record<string, DataRow[]>> = {
      'Electrical Specifications': {},
      'Magnetic Specifications': {},
      'Physical/Operational Specifications': {}
    };
    
    data.data.forEach((row: DataRow) => {
      const category = row.Category;
      const section = determineSection(category);
      
      // Filter by sections if provided
      if (sections && !sections.includes(section)) {
        return;
      }
      
      if (!groups[section][category]) {
        groups[section][category] = [];
      }
      groups[section][category].push(row);
    });
    
    return groups;
  }, [data, sections, determineSection]);

  // Helper function to determine if a row should be highlighted based on focus
  const shouldHighlight = (section: string, category: string, specification: string) => {
    if (!focus) return false;
    
    if (focus.section && focus.section !== section) return false;
    if (focus.category && focus.category !== category) return false;
    if (focus.attribute && !specification.toLowerCase().includes(focus.attribute.toLowerCase())) return false;
    
    return true;
  };

  // Helper function to determine if a value is a diagram path
  const isDiagramField = (specification: string, value: string) => {
    return value.endsWith('.png') || value.endsWith('.jpg') || value.endsWith('.jpeg');
  };

  // Helper function to get relative path from full path
  const getRelativePath = (fullPath: string): string => {
    // Just get the filename without any path
    const filename = fullPath.split(/[/\\]/).pop();
    return `/diagrams/${filename}`;
  };

  // Helper function to render a cell value
  const renderCellValue = (specification: string, value: string | null) => {
    if (!value) return '—';
    
    if (isDiagramField(specification, value)) {
      const relativePath = getRelativePath(value);
      return (
        <div className="flex items-center justify-center m-0 p-0 min-h-0">
          <DiagramThumbnail 
            imagePath={relativePath} 
            alt={`${specification} diagram`}
          />
        </div>
      );
    }
    
    return value;
  };

  // Helper function to determine if a row shows a difference
  const hasDifferences = (row: DataRow): boolean => {
    if (type === 'differences') return false; // Never highlight in differences table
    
    const modelValues = modelColumns
      .map((col: string) => row[col])
      .filter((val: string | null) => val !== null && val !== '');
      
    return modelValues.length >= 2 && new Set(modelValues).size > 1;
  };

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[900px] border border-gray-200 rounded-md shadow-sm">
        <Accordion 
          title={
            <div className="w-full px-4 text-left">{title}</div>
          }
          defaultOpen={true}
          className="border-0 shadow-none rounded-none [&>button]:bg-[#f7941c] [&>button]:text-white [&>button]:hover:bg-[#f7941c]/90"
        >
          <div className="border-t border-gray-200">
            {Object.entries(groupedData).map(([section, categories], sectionIdx) => (
              Object.keys(categories).length > 0 && (
                <div key={`section-${sectionIdx}-${section}`}>
                  <Accordion 
                    title={
                      <div style={{ display: 'grid', gridTemplateColumns: '300px minmax(0px, 1fr) repeat(3, calc(180px + 3rem))', width: '100%', alignItems: 'center' }}>
                        <div className="px-8 py-0.5 text-gray-700 text-left text-sm font-medium">{section}</div>
                        <div></div>
                        {modelColumns.map((model, idx) => (
                          <div key={idx} className="text-sm text-center py-0.5 px-3 pl-12 text-gray-700 font-medium">{model}</div>
                        ))}
                      </div>
                    }
                    defaultOpen={true}
                    className="border-0 shadow-none text-left [&>button]:bg-blue-50 [&>button]:hover:bg-gray-100 [&>button]:py-[1px] [&>button]:rounded-none"
                    variant="inner"
                  >
                    <div className="border-t border-gray-200">
                      {Object.entries(categories).map(([category, rows], categoryIdx) => (
                        <Fragment key={`section-${sectionIdx}-category-${categoryIdx}-${category}`}>
                          <div className={`${focus?.category === category ? 'bg-gray-100' : 'bg-gray-50'} border-b border-gray-200 pl-12`}>
                            <div style={{ display: 'grid', gridTemplateColumns: '300px minmax(0px, 1fr) repeat(3, calc(180px + 3rem))', width: '100%' }}>
                              <div className="px-8 py-0.5 font-semibold text-sm">{category}</div>
                              <div></div>
                            </div>
                          </div>
                          {rows.map((row: DataRow, rowIdx: number) => {
                            const isHighlighted = shouldHighlight(section, category, row.Specification);
                            const showDifference = highlightDifferences && hasDifferences(row);
                            const isLastRow = rowIdx === rows.length - 1 && 
                              categoryIdx === Object.keys(categories).length - 1;
                            
                            return (
                              <div 
                                key={`section-${sectionIdx}-category-${categoryIdx}-row-${rowIdx}`}
                                className={`${
                                  isHighlighted
                                    ? 'bg-yellow-100'
                                    : showDifference
                                      ? 'bg-yellow-50'
                                      : rowIdx % 2 === 0
                                        ? 'bg-white'
                                        : 'bg-gray-50'
                                } ${!isLastRow ? 'border-b' : ''} border-gray-200 pl-16`}
                                style={{ display: 'grid', gridTemplateColumns: '300px minmax(0px, 1fr) repeat(3, calc(180px + 3rem))', width: '100%' }}
                              >
                                <div className="px-8 py-0.5 whitespace-nowrap text-sm text-gray-700">
                                  {row.Specification}
                                </div>
                                <div></div>
                                {modelColumns.map((model: string, modelIdx: number) => {
                                  const value = row[model];
                                  const isDiagram = isDiagramField(row.Specification, value || '');
                                  return (
                                    <div 
                                      key={`section-${sectionIdx}-category-${categoryIdx}-row-${rowIdx}-col-${modelIdx}`}
                                      className={`text-sm text-center text-gray-700 ${
                                        isDiagram ? 'pr-16' : 'pr-16 py-0.5'
                                      }`}
                                    >
                                      {renderCellValue(row.Specification, value)}
                                    </div>
                                  );
                                })}
                              </div>
                            );
                          })}
                        </Fragment>
                      ))}
                    </div>
                  </Accordion>
                </div>
              )
            ))}
          </div>
        </Accordion>
      </div>
    </div>
  );
} 