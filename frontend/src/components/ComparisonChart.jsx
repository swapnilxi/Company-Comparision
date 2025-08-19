"use client";

import React, { useEffect, useState } from 'react';
import { compareCompanies } from '../utils/companyUtils';
import { debounce } from '../utils/helpers.js';

/**
 * Company Comparison Chart Component
 * This is a JavaScript component that uses TypeScript types/interfaces
 * 
 * @param {Object} props - Component props
 * @param {string[]} props.companyIds - Array of company IDs to compare
 * @param {string} props.metric - Metric to compare (employees, revenue, etc.)
 */
const ComparisonChart = ({ companyIds, metric }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Debounced fetch function to prevent too many API calls
  const debouncedFetch = React.useCallback(
    debounce(async (ids) => {
      try {
        setLoading(true);
        const data = await compareCompanies(ids);
        setComparisonData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load comparison data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 500),
    []
  );

  useEffect(() => {
    if (companyIds && companyIds.length > 0) {
      debouncedFetch(companyIds);
    }
  }, [companyIds, debouncedFetch]);

  if (loading) {
    return <div className="p-4 text-center">Loading comparison data...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  if (!comparisonData || !comparisonData.metrics[metric]) {
    return <div className="p-4 text-center">No data available for comparison</div>;
  }

  // Render a simple bar chart
  return (
    <div className="p-4 border rounded-lg bg-white">
      <h3 className="text-lg font-semibold mb-4">Company Comparison: {metric}</h3>
      
      <div className="space-y-4">
        {comparisonData.companies.map((company) => {
          const value = comparisonData.metrics[metric][company.id];
          const maxValue = Math.max(...Object.values(comparisonData.metrics[metric]));
          const percentage = (value / maxValue) * 100;
          
          return (
            <div key={company.id} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>{company.name}</span>
                <span>{typeof value === 'number' ? value.toLocaleString() : value}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full" 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ComparisonChart;