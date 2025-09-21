"use client";

import React, { useEffect, useState } from 'react';

interface ComparableCompany {
  name: string;
  ticker: string;
  rationale: string;
  financial_metrics?: Record<string, any>;
}

interface FilterOptions {
  company_size: Array<{ value: string; label: string }>;
  geography: Array<{ value: string; label: string }>;
  business_characteristics: Array<{ value: string; label: string }>;
  industry_sectors: Array<{ value: string; label: string }>;
}

interface CompanyComparisonTableProps {
  comparableCompanies: ComparableCompany[];
  targetCompany?: {
    name?: string;
    website?: string;
    description?: string;
  };
  targetTicker?: string;
  selectedCompanies: Set<string>;
  onCompanySelectionChange: (selected: Set<string>) => void;
  detailedData?: Record<string, any> | null;
  onRefreshData?: () => void;
  isLoadingDetailed?: boolean;
}

const EnhancedComparisonTable: React.FC<CompanyComparisonTableProps> = ({
  comparableCompanies,
  targetCompany,
  targetTicker,
  selectedCompanies,
  onCompanySelectionChange,
  detailedData: propDetailedData,
  onRefreshData,
  isLoadingDetailed
}) => {
  const [showTargetCompany, setShowTargetCompany] = useState(true);
  const [detailedData, setDetailedData] = useState<Record<string, any> | null>(null);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [filters, setFilters] = useState({
    company_size: [] as string[],
    geography: [] as string[],
    business_characteristics: [] as string[],
    industry_sectors: [] as string[]
  });
  const [showFilters, setShowFilters] = useState(true);

  // Fetch filter options on component mount
  useEffect(() => {
    fetchFilterOptions();
  }, []);

  // Use prop detailed data if available
  useEffect(() => {
    if (propDetailedData) {
      setDetailedData(propDetailedData);
    }
  }, [propDetailedData]);

  const fetchFilterOptions = async () => {
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${API_BASE}/api/filter-options`);
      if (response.ok) {
        const data = await response.json();
        setFilterOptions(data);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const toggleCompanySelection = (ticker: string) => {
    const newSelection = new Set(selectedCompanies);
    if (newSelection.has(ticker)) {
      newSelection.delete(ticker);
    } else {
      newSelection.add(ticker);
    }
    onCompanySelectionChange(newSelection);
  };

  const selectAllCompanies = () => {
    onCompanySelectionChange(new Set(comparableCompanies.map(c => c.ticker)));
  };

  const clearSelection = () => {
    onCompanySelectionChange(new Set());
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined || value === "N/A") return '-';
    if (typeof value === 'number') {
      if (value >= 1000000000) {
        return `$${(value / 1000000000).toFixed(2)}B`;
      } else if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(2)}M`;
      } else if (value >= 1000) {
        return `$${(value / 1000).toFixed(2)}K`;
      }
      return value.toLocaleString();
    }
    return String(value);
  };

  const formatPercentage = (value: any): string => {
    if (value === null || value === undefined || value === "N/A") return '-';
    if (typeof value === 'number') {
      return `${value.toFixed(2)}%`;
    }
    return String(value);
  };

  const getComparisonData = () => {
    const companies = [];
    
    // Add target company if available and selected
    if (targetCompany && showTargetCompany) {
      companies.push({
        name: targetCompany.name || 'Target Company',
        ticker: targetTicker || 'TARGET',
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

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      if (newFilters[filterType as keyof typeof filters].includes(value)) {
        newFilters[filterType as keyof typeof filters] = newFilters[filterType as keyof typeof filters].filter(v => v !== value);
      } else {
        newFilters[filterType as keyof typeof filters] = [...newFilters[filterType as keyof typeof filters], value];
      }
      return newFilters;
    });
  };

  const clearFilters = () => {
    setFilters({
      company_size: [],
      geography: [],
      business_characteristics: [],
      industry_sectors: []
    });
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
      {/* Filters Section */}
      {filterOptions && (
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Filters
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-3 py-1 text-sm bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                {showFilters ? 'Hide' : 'Show'} Filters
              </button>
              <button
                onClick={clearFilters}
                className="px-3 py-1 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Company Size Filter */}
              <div>
                <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Company Size</h4>
                <div className="space-y-1">
                  {filterOptions.company_size.map(option => (
                    <label key={option.value} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.company_size.includes(option.value)}
                        onChange={() => handleFilterChange('company_size', option.value)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-600 dark:text-gray-400">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Geography Filter */}
              <div>
                <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Geography</h4>
                <div className="space-y-1">
                  {filterOptions.geography.map(option => (
                    <label key={option.value} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.geography.includes(option.value)}
                        onChange={() => handleFilterChange('geography', option.value)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-600 dark:text-gray-400">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Business Characteristics Filter */}
              <div>
                <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Business Model</h4>
                <div className="space-y-1">
                  {filterOptions.business_characteristics.map(option => (
                    <label key={option.value} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.business_characteristics.includes(option.value)}
                        onChange={() => handleFilterChange('business_characteristics', option.value)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-600 dark:text-gray-400">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Industry Sectors Filter */}
              <div>
                <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Industry</h4>
                <div className="space-y-1">
                  {filterOptions.industry_sectors.map(option => (
                    <label key={option.value} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.industry_sectors.includes(option.value)}
                        onChange={() => handleFilterChange('industry_sectors', option.value)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-600 dark:text-gray-400">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

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
            {onRefreshData && (
              <button
                onClick={onRefreshData}
                disabled={isLoadingDetailed}
                className="p-2 text-gray-600 hover:text-blue-600 transition-colors disabled:opacity-50"
                title="Refresh data"
              >
                {isLoadingDetailed ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )}
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
                {/* Basic Information */}
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

                {/* Market Data */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Current Price
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const price = companyData?.quote?.price;
                    return (
                      <td
                        key={`price-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {price ? `$${price.toFixed(2)}` : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Market Cap
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const marketCap = companyData?.profile?.mktCap;
                    return (
                      <td
                        key={`marketcap-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {marketCap ? formatValue(marketCap) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Financial Metrics */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Revenue
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const revenue = companyData?.profile?.revenue;
                    return (
                      <td
                        key={`revenue-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {revenue ? formatValue(revenue) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    EBITDA
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const ebitda = companyData?.profile?.ebitda;
                    return (
                      <td
                        key={`ebitda-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {ebitda ? formatValue(ebitda) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Net Income
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const netIncome = companyData?.profile?.netIncome;
                    return (
                      <td
                        key={`netincome-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {netIncome ? formatValue(netIncome) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Valuation Ratios */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    P/E Ratio
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const peRatio = companyData?.ratios?.priceEarningsRatio;
                    return (
                      <td
                        key={`pe-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {peRatio ? peRatio.toFixed(2) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    P/B Ratio
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const pbRatio = companyData?.ratios?.priceToBookRatio;
                    return (
                      <td
                        key={`pb-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {pbRatio ? pbRatio.toFixed(2) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Profitability Ratios */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    ROE
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
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
                        {roe ? formatPercentage(roe * 100) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    ROA
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
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
                        {roa ? formatPercentage(roa * 100) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Margin Ratios */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Gross Margin
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const grossMargin = companyData?.ratios?.grossProfitMargin;
                    return (
                      <td
                        key={`gross-margin-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {grossMargin ? formatPercentage(grossMargin * 100) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Operating Margin
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const operatingMargin = companyData?.ratios?.operatingProfitMargin;
                    return (
                      <td
                        key={`operating-margin-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {operatingMargin ? formatPercentage(operatingMargin * 100) : '-'}
                      </td>
                    );
                  })}
                </tr>

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Net Margin
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const netMargin = companyData?.ratios?.netProfitMargin;
                    return (
                      <td
                        key={`net-margin-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {netMargin ? formatPercentage(netMargin * 100) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Liquidity Ratios */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Current Ratio
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
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

                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Quick Ratio
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
                      (d: any) => d.ticker === company.ticker
                    );
                    const quickRatio = companyData?.ratios?.quickRatio;
                    return (
                      <td
                        key={`quick-ratio-${company.ticker}`}
                        className={`px-4 py-3 text-sm text-gray-900 dark:text-gray-100 ${
                          company.type === 'target' ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        {quickRatio ? quickRatio.toFixed(2) : '-'}
                      </td>
                    );
                  })}
                </tr>

                {/* Leverage Ratios */}
                <tr>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700/30">
                    Debt to Equity
                  </td>
                  {comparisonData.map((company) => {
                    const companyData = detailedData?.comparison_data?.find(
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

export default EnhancedComparisonTable;
