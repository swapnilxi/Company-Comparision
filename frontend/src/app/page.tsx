"use client";

import React from "react";
import EnhancedComparisonTable from "../components/EnhancedComparisonTable";

type ComparableCompany = {
  name: string;
  ticker: string;
  rationale: string;
  financial_metrics?: Record<string, any> | undefined;
};

type FindComparablesResponse = {
  target_company: {
    id?: string | null;
    name?: string | null;
    website?: string | null;
    description?: string | null;
  };
  comparable_companies: ComparableCompany[];
  financial_data_included?: boolean;
  note?: string;
  analysis_timestamp?: string;
  input_type?: string;
};

type CompanyAnalysisResponse = {
  name: string;
  website: string;
  description: string;
  industry?: string | null;
  business_model?: string | null;
  products_or_services?: string | null;
  target_market?: string | null;
  company_size?: string | null;
  geographic_presence?: string | null;
  key_differentiators?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const [companyName, setCompanyName] = React.useState("");
  const [companyWebsite, setCompanyWebsite] = React.useState("");
  const [companyId, setCompanyId] = React.useState("");
  const [ticker, setTicker] = React.useState("");
  const [count, setCount] = React.useState<number>(10);
  const [loadingAction, setLoadingAction] = React.useState<null | "analyze" | "compare" | "compare_fin">(null);
  const [error, setError] = React.useState<string | null>(null);
  const [analysis, setAnalysis] = React.useState<CompanyAnalysisResponse | null>(null);
  const [comparables, setComparables] = React.useState<FindComparablesResponse | null>(null);
  const [activeTab, setActiveTab] = React.useState<"results" | "comparison">("results");
  const [selectedCompanies, setSelectedCompanies] = React.useState<Set<string>>(new Set());
  const [filterOptions, setFilterOptions] = React.useState<any>(null);
  const [filters, setFilters] = React.useState({
    company_size: [] as string[],
    geography: [] as string[],
    business_characteristics: [] as string[],
    industry_sectors: [] as string[]
  });
  const [showFilters, setShowFilters] = React.useState(true);
  const [detailedData, setDetailedData] = React.useState<Record<string, any> | null>(null);

  async function fetchProfileByTicker(symbol: string): Promise<void> {
    if (!symbol) return;
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/market/profile/${encodeURIComponent(symbol)}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const name = data?.companyName || "";
      let website = data?.website || "";
      if (website && !website.startsWith("http")) website = `https://${website}`;
      if (name && !companyName) setCompanyName(name);
      if (website && !companyWebsite) setCompanyWebsite(website);
    } catch (err: any) {
      setError(`Failed to fetch profile: ${err?.message || "Unknown error"}`);
    }
  }

  async function analyzeAction() {
    setError(null);
    setAnalysis(null);
    setComparables(null);
    setLoadingAction("analyze");
    try {
      const name = companyName.trim();
      const website = companyWebsite.trim();

      if (name && website) {
        // Use strict analyze when both provided
        const res = await fetch(`${API_BASE}/api/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, website }),
        });
        if (!res.ok) throw new Error(await res.text());
        const data = (await res.json()) as CompanyAnalysisResponse;
        setAnalysis(data);
      } else {
        // Fallback to flexible endpoint using any of ticker | name | website | company_id
        const body: Record<string, any> = { count: 10 };
        if (ticker) body.ticker = ticker.trim();
        else if (name && website) {
          body.company_name = name;
          body.company_website = website;
        } else if (name) body.company_name = name;
        else if (website) body.company_website = website;
        else if (companyId) body.company_id = companyId.trim();

        const res = await fetch(`${API_BASE}/api/find-comparables`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(await res.text());
        const data = (await res.json()) as FindComparablesResponse;
        // Map to analysis structure from target_company
        const tc = data?.target_company || {};
        setAnalysis({
          name: (tc.name as string) || "",
          website: (tc.website as string) || "",
          description: (tc.description as string) || "",
        });
        setComparables(data);
      }
    } catch (err: any) {
      setError(err?.message || "Unknown error");
    } finally {
      setLoadingAction(null);
    }
  }

  async function compareAction(withFinancials: boolean) {
    setError(null);
    setComparables(null);
    setLoadingAction(withFinancials ? "compare_fin" : "compare");
    try {
      const headers = { "Content-Type": "application/json" };
      const body: Record<string, any> = { count };

      // Priority: ticker > name+website > name > website > company_id (only allowed if without financials)
      if (ticker) {
        body.ticker = ticker.trim();
      } else if (companyName && companyWebsite) {
        body.company_name = companyName.trim();
        body.company_website = companyWebsite.trim();
      } else if (companyName) {
        body.company_name = companyName.trim();
      } else if (companyWebsite) {
        body.company_website = companyWebsite.trim();
      } else if (!withFinancials && companyId) {
        body.company_id = companyId.trim();
      }

      const endpoint = withFinancials
        ? `${API_BASE}/api/comparables-with-financials`
        : `${API_BASE}/api/find-comparables`;

      const res = await fetch(endpoint, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }
      const data = (await res.json()) as FindComparablesResponse;
      setComparables(data);
    } catch (err: any) {
      setError(err?.message || "Unknown error");
    } finally {
      setLoadingAction(null);
    }
  }

  const handleCompanySelection = (ticker: string) => {
    const newSelection = new Set(selectedCompanies);
    if (newSelection.has(ticker)) {
      newSelection.delete(ticker);
    } else {
      newSelection.add(ticker);
    }
    setSelectedCompanies(newSelection);
  };

  const handleCompareSelected = async () => {
    if (selectedCompanies.size > 0) {
      setActiveTab("comparison");
      // Auto-fetch detailed data when switching to comparison tab
      await fetchDetailedDataForSelected();
    }
  };

  const fetchDetailedDataForSelected = async () => {
    if (selectedCompanies.size === 0) return;
    
    setLoadingAction("compare");
    try {
      const tickers = Array.from(selectedCompanies);
      console.log('Fetching detailed data for tickers:', tickers);
      
      const response = await fetch(`${API_BASE}/api/detailed-comparison`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers,
          include_ratios: true,
          include_statements: false,
          filters
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', errorText);
        throw new Error(`Failed to fetch detailed data: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Received detailed data:', data);
      setDetailedData(data);
      setError(null); // Clear any previous errors
    } catch (error) {
      console.error('Error fetching detailed data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch detailed comparison data');
    } finally {
      setLoadingAction(null);
    }
  };

  // Fetch filter options on component mount
  React.useEffect(() => {
    fetchFilterOptions();
  }, []);

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/filter-options`);
      if (response.ok) {
        const data = await response.json();
        setFilterOptions(data);
      }
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
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

  const getFilteredCompanies = () => {
    if (!comparables?.comparable_companies) return [];
    
    // Return all companies for now - filtering is done on the backend
    return comparables.comparable_companies;
  };

  const hasValidValue = (value: any): boolean => {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string' && (value.toLowerCase() === 'n/a' || value.toLowerCase() === 'null' || value.trim() === '')) return false;
    if (typeof value === 'number' && (isNaN(value) || !isFinite(value))) return false;
    return true;
  };

  const getValidFinancialMetrics = (metrics: Record<string, any> | undefined): Record<string, any> => {
    if (!metrics) return {};
    const validMetrics: Record<string, any> = {};
    Object.entries(metrics).forEach(([key, value]) => {
      if (hasValidValue(value)) {
        validMetrics[key] = value;
      }
    });
    return validMetrics;
  };

  const applyFilters = async () => {
    if (!comparables) return;
    
    setLoadingAction("compare");
    try {
      const headers = { "Content-Type": "application/json" };
      const body: Record<string, any> = { 
        count,
        filters
      };

      // Priority: ticker > name+website > name > website > company_id
      if (ticker) {
        body.ticker = ticker.trim();
      } else if (companyName && companyWebsite) {
        body.company_name = companyName.trim();
        body.company_website = companyWebsite.trim();
      } else if (companyName) {
        body.company_name = companyName.trim();
      } else if (companyWebsite) {
        body.company_website = companyWebsite.trim();
      } else if (companyId) {
        body.company_id = companyId.trim();
      }

      const res = await fetch(`${API_BASE}/api/find-comparables`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }
      const data = (await res.json()) as FindComparablesResponse;
      setComparables(data);
      // Clear selections and detailed data when filters are applied
      setSelectedCompanies(new Set());
      setDetailedData(null);
    } catch (err: any) {
      setError(err?.message || "Unknown error");
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="font-sans min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
      <main className="max-w-6xl mx-auto p-8 pb-20 sm:p-20">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Company Comparables Finder
          </h1>
          <p className="text-gray-600 dark:text-gray-300">Discover comparable companies with AI-powered analysis</p>
        </div>

        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-8">
          <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Ticker</label>
                <div className="flex gap-2">
                  <input
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white/50 dark:bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="e.g., AAPL"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    onBlur={() => fetchProfileByTicker(ticker)}
                  />
                  <button
                    type="button"
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 transition-all"
                    onClick={() => fetchProfileByTicker(ticker)}
                  >
                    Autofill
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">If provided, ticker takes priority.</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Company Name</label>
                <input
                  className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white/50 dark:bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="e.g., Tech Innovations Inc."
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Company Website</label>
                <input
                  className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white/50 dark:bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="https://example.com"
                  value={companyWebsite}
                  onChange={(e) => setCompanyWebsite(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Company ID (DB code, optional)</label>
                <input
                  className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white/50 dark:bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Only used when Financials is OFF"
                  value={companyId}
                  onChange={(e) => setCompanyId(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-700 dark:text-gray-300">Count</label>
                <input
                  type="number"
                  min={1}
                  max={20}
                  className="w-20 border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 bg-white/50 dark:bg-gray-700/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  value={count}
                  onChange={(e) => setCount(Number(e.target.value))}
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                disabled={loadingAction === "analyze"}
                onClick={analyzeAction}
              >
                {loadingAction === "analyze" ? (
                  <span className="inline-flex items-center gap-2"><span className="inline-block h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> Analyzing...</span>
                ) : (
                  "Analyze"
                )}
              </button>
              <button
                type="button"
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                disabled={loadingAction === "compare"}
                onClick={() => compareAction(false)}
              >
                {loadingAction === "compare" ? (
                  <span className="inline-flex items-center gap-2"><span className="inline-block h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> Comparing...</span>
                ) : (
                  "Compare"
                )}
              </button>
              <button
                type="button"
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                disabled={loadingAction === "compare_fin"}
                onClick={() => compareAction(true)}
              >
                {loadingAction === "compare_fin" ? (
                  <span className="inline-flex items-center gap-2"><span className="inline-block h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> Comparing...</span>
                ) : (
                  "Compare + Financials"
                )}
              </button>
              <button
                type="button"
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-gray-500 to-gray-600 text-white hover:from-gray-600 hover:to-gray-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                onClick={() => { setAnalysis(null); setComparables(null); setError(null); }}
              >
                Clear
              </button>
            </div>
          </form>
        </div>

        {error && (
          <div className="p-4 border border-red-300 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-xl mb-6 shadow-lg">
            {error}
          </div>
        )}

        {analysis && (
          <section className="space-y-4 mb-8">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
              <h2 className="text-xl font-semibold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Analysis</h2>
              <div className="text-sm space-y-3">
                <div className="flex flex-wrap gap-4">
                  <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Name:</span> <span className="break-words text-gray-900 dark:text-gray-100">{analysis.name}</span></div>
                  <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Website:</span> <span className="break-all text-blue-600 dark:text-blue-400">{analysis.website}</span></div>
                </div>
                <div className="whitespace-pre-wrap break-words text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">{analysis.description}</div>
                <div className="flex flex-wrap gap-4">
                  {analysis.industry && <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Industry:</span> <span className="break-words text-gray-900 dark:text-gray-100">{analysis.industry}</span></div>}
                  {analysis.business_model && <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Business Model:</span> <span className="break-words text-gray-900 dark:text-gray-100">{analysis.business_model}</span></div>}
                </div>
                {analysis.products_or_services && <div className="break-words"><span className="font-medium text-gray-700 dark:text-gray-300">Products/Services:</span> <span className="text-gray-900 dark:text-gray-100">{analysis.products_or_services}</span></div>}
                {analysis.target_market && <div className="break-words"><span className="font-medium text-gray-700 dark:text-gray-300">Target Market:</span> <span className="text-gray-900 dark:text-gray-100">{analysis.target_market}</span></div>}
                <div className="flex flex-wrap gap-4">
                  {analysis.company_size && <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Company Size:</span> <span className="break-words text-gray-900 dark:text-gray-100">{analysis.company_size}</span></div>}
                  {analysis.geographic_presence && <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Geographic Presence:</span> <span className="break-words text-gray-900 dark:text-gray-100">{analysis.geographic_presence}</span></div>}
                </div>
                {analysis.key_differentiators && <div className="break-words"><span className="font-medium text-gray-700 dark:text-gray-300">Key Differentiators:</span> <span className="text-gray-900 dark:text-gray-100">{analysis.key_differentiators}</span></div>}
              </div>
            </div>
          </section>
        )}

        {comparables && (
          <section className="space-y-6">
            {/* Tab Navigation */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-2">
              <div className="flex space-x-1">
                              <button
                onClick={() => {
                  setActiveTab("results");
                  setDetailedData(null);
                }}
                className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "results"
                    ? "bg-blue-500 text-white shadow-lg"
                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                Results View
              </button>
              <button
                onClick={() => setActiveTab("comparison")}
                className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "comparison"
                    ? "bg-blue-500 text-white shadow-lg"
                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                Comparison Table
              </button>
              </div>
            </div>

            {activeTab === "results" && (
              <>
                {/* Filters Section */}
                {filterOptions && (
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-4 mb-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        Filter Comparable Companies
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
                        <button
                          onClick={applyFilters}
                          disabled={loadingAction === "compare"}
                          className="px-3 py-1 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                        >
                          {loadingAction === "compare" ? "Applying..." : "Apply Filters"}
                        </button>
                      </div>
                    </div>

                    {showFilters && (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Company Size Filter */}
                        <div>
                          <h4 className="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2">Company Size</h4>
                          <div className="space-y-1">
                            {filterOptions.company_size.map((option: any) => (
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
                            {filterOptions.geography.map((option: any) => (
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
                            {filterOptions.business_characteristics.map((option: any) => (
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
                            {filterOptions.industry_sectors.map((option: any) => (
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

                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
                  <h2 className="text-xl font-semibold mb-4 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">Target Company</h2>
                  <div className="text-sm space-y-3">
                    <div className="flex flex-wrap gap-4">
                      <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Name:</span> <span className="break-words text-gray-900 dark:text-gray-100">{comparables.target_company?.name || "-"}</span></div>
                      <div className="flex-1 min-w-0"><span className="font-medium text-gray-700 dark:text-gray-300">Website:</span> <span className="break-all text-blue-600 dark:text-blue-400">{comparables.target_company?.website || "-"}</span></div>
                    </div>
                    <div className="whitespace-pre-wrap break-words text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">{comparables.target_company?.description || ""}</div>
                  </div>
                </div>

                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">Comparable Companies</h2>
                    {selectedCompanies.size > 0 && (
                      <button
                        onClick={handleCompareSelected}
                        disabled={loadingAction === "compare"}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                      >
                        {loadingAction === "compare" ? (
                          <span className="inline-flex items-center gap-2">
                            <span className="inline-block h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                            Loading...
                          </span>
                        ) : (
                          `Compare Selected (${selectedCompanies.size})`
                        )}
                      </button>
                    )}
                  </div>
                  {getFilteredCompanies().length ? (
                    <ul className="space-y-4 max-w-full">
                      {getFilteredCompanies().map((c, idx) => (
                        <li key={`${c.ticker}-${idx}`} className="p-4 border border-gray-200 dark:border-gray-600 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 overflow-hidden hover:shadow-lg transition-all">
                          <div className="flex items-start gap-3">
                            <input
                              type="checkbox"
                              checked={selectedCompanies.has(c.ticker)}
                              onChange={() => handleCompanySelection(c.ticker)}
                              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <div className="flex-1">
                              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                                <div className="font-medium break-words flex-1 min-w-0 text-gray-900 dark:text-gray-100">{c.name}</div>
                                <div className="text-sm text-gray-600 dark:text-gray-400 flex-shrink-0 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">{c.ticker}</div>
                              </div>
                              <div className="text-sm whitespace-pre-wrap break-words text-gray-700 dark:text-gray-300">{c.rationale}</div>
                              {(() => {
                                const validMetrics = getValidFinancialMetrics(c.financial_metrics);
                                return Object.keys(validMetrics).length > 0 && (
                                  <div className="mt-3 flex flex-wrap gap-2 text-sm">
                                    {Object.entries(validMetrics).map(([k, v]) => (
                                      <div key={k} className="border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 flex-shrink-0 bg-white/50 dark:bg-gray-700/50">
                                        <span className="font-medium mr-1 break-words text-gray-700 dark:text-gray-300">{k}:</span>
                                        <span className="break-words text-gray-900 dark:text-gray-100">{String(v)}</span>
                                      </div>
                                    ))}
                                  </div>
                                );
                              })()}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {comparables.comparable_companies?.length ? 
                        "No companies match the selected filters." : 
                        "No comparable companies found."
                      }
                    </div>
                  )}
                </div>
              </>
            )}

            {activeTab === "comparison" && (
              <EnhancedComparisonTable
                comparableCompanies={comparables.comparable_companies || []}
                targetCompany={{
                  name: comparables.target_company?.name || undefined,
                  website: comparables.target_company?.website || undefined,
                  description: comparables.target_company?.description || undefined
                }}
                selectedCompanies={selectedCompanies}
                onCompanySelectionChange={setSelectedCompanies}
                detailedData={detailedData}
                onRefreshData={fetchDetailedDataForSelected}
                isLoadingDetailed={loadingAction === "compare"}
              />
            )}
          </section>
        )}
      </main>
    </div>
  );
}
