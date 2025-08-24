"use client";

import React, { useEffect, useState } from 'react';

interface ComparableCompany {
  name: string;
  ticker: string;
  rationale: string;
  financial_metrics?: Record<string, any>;
}

interface CompanyComparisonTableProps {
  comparableCompanies: ComparableCompany[];
  targetCompany?: {
    name?: string;
    website?: string;
    description?: string;
  };
}

const CompanyComparisonTable: React.FC<CompanyComparisonTableProps> = ({
  comparableCompanies,
  targetCompany
}) => {
  const [selectedCompanies, setSelectedCompanies] = useState<Set<string>>(new Set());
  const [showTargetCompany, setShowTargetCompany] = useState(true);
  const [detailedData, setDetailedData] = useState<Record<string, any> | null>(null);
  const [loadingDetailed, setLoadingDetailed] = useState(false);

  // Auto-select first few companies for better UX
  useEffect(() => {
    if (comparableCompanies.length > 0 && selectedCompanies.size === 0) {
      const initialSelection = new Set(comparableCompanies.slice(0, 3).map(c => c.ticker));
      setSelectedCompanies(initialSelection);
    }
  }, [comparableCompanies]);

  const toggleCompanySelection = (ticker: string) => {
    const newSelection = new Set(selectedCompanies);
    if (newSelection.has(ticker)) {
      newSelection.delete(ticker);
    } else {
      newSelection.add(ticker);
    }
    setSelectedCompanies(newSelection);
  };

  const selectAllCompanies = () => {
    setSelectedCompanies(new Set(comparableCompanies.map(c => c.ticker)));
  };

  const clearSelection = () => {
    setSelectedCompanies(new Set());
  };

  const fetchDetailedData = async () => {
    if (selectedCompanies.size === 0) return;
    
    setLoadingDetailed(true);
    try {
      const tickers = Array.from(selectedCompanies);
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${API_BASE}/api/detailed-comparison`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers,
          include_ratios: true,
          include_statements: false
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch detailed data');
      }
      
      const data = await response.json();
      setDetailedData(data);
    } catch (error) {
      console.error('Error fetching detailed data:', error);
    } finally {
      setLoadingDetailed(false);
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(2)}M`;
      } else if (value >= 1000) {
        return `$${(value / 1000).toFixed(2)}K`;
      }
      return value.toLocaleString();
    }
    return String(value);
  };

  const getComparisonData = () => {
    const companies = [];
    
    // Add target company if available and selected
    if (targetCompany && showTargetCompany) {
      companies.push({
        name: targetCompany.name || 'Target Company',
        ticker: 'TARGET',
        type: 'target',
        description: targetCompany.description || '',
        website: targetCompany.website || '',
        rationale: 'Base company for comparison'
      });
    }

    // Add selected comparable companies
    comparableCompanies.forEach(company => {
      if (selectedCompanies.has(company.ticker)) {
        companies.push({
          ...company,
          type: 'comparable'
        });
      }
    });

    return companies;
  };

  const comparisonData = getComparisonData();

  if (comparableCompanies.length === 0) {
    return (
      <div className="p-6 text-center text-gray-500">
        No comparable companies available for comparison.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Selection Controls */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-4">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Select Companies to Compare
          </h3>
          <div className="flex gap-2">
            <button
              onClick={selectAllCompanies}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Select All
            </button>
            <button
              onClick={clearSelection}
              className="px-3 py-1 text-sm bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              Clear
            </button>
            {selectedCompanies.size > 0 && (
              <button
                onClick={fetchDetailedData}
                disabled={loadingDetailed}
                className="px-3 py-1 text-sm bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
              >
                {loadingDetailed ? 'Loading...' : 'Get Detailed Data'}
              </button>
            )}
          </div>
        </div>

        {/* Target Company Toggle */}
        {targetCompany && (
          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showTargetCompany}
                onChange={(e) => setShowTargetCompany(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Include Target Company in Comparison
              </span>
            </label>
          </div>
        )}

        {/* Company Selection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {comparableCompanies.map((company) => (
            <label
              key={company.ticker}
              className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                selectedCompanies.has(company.ticker)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 bg-white/50 dark:bg-gray-700/50'
              }`}
            >
              <input
                type="checkbox"
                checked={selectedCompanies.has(company.ticker)}
                onChange={() => toggleCompanySelection(company.ticker)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
                  {company.name}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {company.ticker}
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      {comparisonData.length > 0 && (
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Company Comparison Table
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Comparing {comparisonData.length} companies
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Parameter
                  </th>
                  {comparisonData.map((company) => (
                    <th
                      key={company.ticker}
                      className={`px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${
                        company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="font-semibold text-gray-900 dark:text-gray-100">
                          {company.name}
                        </div>
                        <div className="text-xs">
                          {company.type === 'target' ? 'Target' : company.ticker}
                        </div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                {/* Company Name */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Company Name
                  </td>
                  {comparisonData.map((company) => (
                    <td
                      key={`name-${company.ticker}`}
                      className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                        company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      {company.name}
                    </td>
                  ))}
                </tr>

                {/* Ticker Symbol */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Ticker Symbol
                  </td>
                  {comparisonData.map((company) => (
                    <td
                      key={`ticker-${company.ticker}`}
                      className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                        company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      {company.type === 'target' ? '-' : company.ticker}
                    </td>
                  ))}
                </tr>

                {/* Website */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Website
                  </td>
                  {comparisonData.map((company) => (
                    <td
                      key={`website-${company.ticker}`}
                      className={`px-4 py-3 text-sm ${
                        company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      {company.website ? (
                        <a
                          href={company.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 dark:text-blue-400 hover:underline break-all"
                        >
                          {company.website}
                        </a>
                      ) : (
                        <span className="text-gray-500 dark:text-gray-400">-</span>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Description */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Description
                  </td>
                  {comparisonData.map((company) => (
                    <td
                      key={`description-${company.ticker}`}
                      className={`px-4 py-3 text-sm text-gray-700 dark:text-gray-300 ${
                        company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      <div className="max-w-xs">
                        {company.description || company.rationale || '-'}
                      </div>
                    </td>
                  ))}
                </tr>

                {/* Financial Metrics */}
                {comparisonData.some(c => c.financial_metrics) && (
                  <>
                    {/* Market Cap */}
                    <tr>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                        Market Cap
                      </td>
                      {comparisonData.map((company) => (
                        <td
                          key={`marketcap-${company.ticker}`}
                          className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                            company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          }`}
                        >
                          {company.financial_metrics?.marketCap 
                            ? formatValue(company.financial_metrics.marketCap)
                            : '-'
                          }
                        </td>
                      ))}
                    </tr>

                    {/* Revenue */}
                    <tr>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                        Revenue
                      </td>
                      {comparisonData.map((company) => (
                        <td
                          key={`revenue-${company.ticker}`}
                          className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                            company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          }`}
                        >
                          {company.financial_metrics?.revenue 
                            ? formatValue(company.financial_metrics.revenue)
                            : '-'
                          }
                        </td>
                      ))}
                    </tr>

                    {/* EBITDA */}
                    <tr>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                        EBITDA
                      </td>
                      {comparisonData.map((company) => (
                        <td
                          key={`ebitda-${company.ticker}`}
                          className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                            company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          }`}
                        >
                          {company.financial_metrics?.ebitda 
                            ? formatValue(company.financial_metrics.ebitda)
                            : '-'
                          }
                        </td>
                      ))}
                    </tr>

                    {/* Price to Earnings Ratio */}
                    <tr>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                        P/E Ratio
                      </td>
                      {comparisonData.map((company) => (
                        <td
                          key={`pe-${company.ticker}`}
                          className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                            company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                          }`}
                        >
                          {company.financial_metrics?.peRatio 
                            ? formatValue(company.financial_metrics.peRatio)
                            : '-'
                          }
                        </td>
                      ))}
                    </tr>
                  </>
                )}

                                 {/* Additional Financial Metrics */}
                 {comparisonData.some(c => c.financial_metrics) && 
                  Object.keys(comparisonData[0]?.financial_metrics || {}).length > 4 && (
                   <>
                     {Object.keys(comparisonData[0]?.financial_metrics || {})
                       .filter(key => !['marketCap', 'revenue', 'ebitda', 'peRatio'].includes(key))
                       .map(metricKey => (
                         <tr key={metricKey}>
                           <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                             {metricKey.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                           </td>
                           {comparisonData.map((company) => (
                             <td
                               key={`${metricKey}-${company.ticker}`}
                               className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                                 company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                               }`}
                             >
                               {company.financial_metrics?.[metricKey] 
                                 ? formatValue(company.financial_metrics[metricKey])
                                 : '-'
                               }
                             </td>
                           ))}
                         </tr>
                       ))}
                   </>
                 )}

                 {/* Detailed Financial Ratios (if available) */}
                 {detailedData && (
                   <>
                     {/* ROE */}
                     <tr>
                       <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                         Return on Equity
                       </td>
                       {comparisonData.map((company) => {
                         const companyData = detailedData.comparison_data?.find(
                           (d: any) => d.ticker === company.ticker
                         );
                         const roe = companyData?.ratios?.returnOnEquity;
                         return (
                           <td
                             key={`roe-${company.ticker}`}
                             className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                               company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                             }`}
                           >
                             {roe ? `${(roe * 100).toFixed(2)}%` : '-'}
                           </td>
                         );
                       })}
                     </tr>

                     {/* ROA */}
                     <tr>
                       <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                         Return on Assets
                       </td>
                       {comparisonData.map((company) => {
                         const companyData = detailedData.comparison_data?.find(
                           (d: any) => d.ticker === company.ticker
                         );
                         const roa = companyData?.ratios?.returnOnAssets;
                         return (
                           <td
                             key={`roa-${company.ticker}`}
                             className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                               company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                             }`}
                           >
                             {roa ? `${(roa * 100).toFixed(2)}%` : '-'}
                           </td>
                         );
                       })}
                     </tr>

                     {/* Debt to Equity */}
                     <tr>
                       <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                         Debt to Equity
                       </td>
                       {comparisonData.map((company) => {
                         const companyData = detailedData.comparison_data?.find(
                           (d: any) => d.ticker === company.ticker
                         );
                         const debtToEquity = companyData?.ratios?.debtEquityRatio;
                         return (
                           <td
                             key={`debt-equity-${company.ticker}`}
                             className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                               company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                             }`}
                           >
                             {debtToEquity ? debtToEquity.toFixed(2) : '-'}
                           </td>
                         );
                       })}
                     </tr>

                     {/* Current Ratio */}
                     <tr>
                       <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                         Current Ratio
                       </td>
                       {comparisonData.map((company) => {
                         const companyData = detailedData.comparison_data?.find(
                           (d: any) => d.ticker === company.ticker
                         );
                         const currentRatio = companyData?.ratios?.currentRatio;
                         return (
                           <td
                             key={`current-ratio-${company.ticker}`}
                             className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                               company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                             }`}
                           >
                             {currentRatio ? currentRatio.toFixed(2) : '-'}
                           </td>
                         );
                       })}
                     </tr>

                     {/* Price to Book */}
                     <tr>
                       <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                         Price to Book
                       </td>
                       {comparisonData.map((company) => {
                         const companyData = detailedData.comparison_data?.find(
                           (d: any) => d.ticker === company.ticker
                         );
                         const pbRatio = companyData?.ratios?.priceToBookRatio;
                         return (
                           <td
                             key={`pb-ratio-${company.ticker}`}
                             className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                               company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                             }`}
                           >
                             {pbRatio ? pbRatio.toFixed(2) : '-'}
                           </td>
                         );
                       })}
                     </tr>
                   </>
                 )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* No Companies Selected Message */}
      {selectedCompanies.size === 0 && (
        <div className="p-6 text-center text-gray-500 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20">
          Please select at least one company to view the comparison table.
        </div>
      )}
    </div>
  );
};

export default CompanyComparisonTable;
