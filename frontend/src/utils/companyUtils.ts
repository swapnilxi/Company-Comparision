/**
 * TypeScript utilities for company comparison functionality
 */
import { fetchData } from './helpers.js';

/**
 * Company information interface
 */
export interface CompanyInfo {
  id: string;
  name: string;
  industry: string;
  founded: number;
  employees: number;
  revenue?: number;
  description?: string;
}

/**
 * Comparison result interface
 */
export interface ComparisonResult {
  companies: CompanyInfo[];
  metrics: {
    [key: string]: {
      [companyId: string]: number | string;
    };
  };
  timestamp: Date;
}

/**
 * Mock company data for demonstration
 */
const mockCompanies: Record<string, CompanyInfo> = {
  "company1": {
    id: "company1",
    name: "Tech Innovations Inc.",
    industry: "Technology",
    founded: 2010,
    employees: 1200,
    revenue: 5000000,
    description: "A leading technology company specializing in AI solutions."
  },
  "company2": {
    id: "company2",
    name: "Global Finance Group",
    industry: "Finance",
    founded: 1995,
    employees: 3500,
    revenue: 12000000,
    description: "International financial services provider."
  }
};

/**
 * Fetch company information
 * @param companyId - The ID of the company to fetch
 * @returns Promise with company information
 */
export async function getCompanyInfo(companyId: string): Promise<CompanyInfo> {
  // Use mock data instead of API call to avoid 404 errors
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const company = mockCompanies[companyId];
      if (company) {
        resolve(company);
      } else {
        reject(new Error(`Company with ID ${companyId} not found`));
      }
    }, 300); // Simulate network delay
  });
}

/**
 * Compare multiple companies
 * @param companyIds - Array of company IDs to compare
 * @returns Promise with comparison results
 */
export async function compareCompanies(companyIds: string[]): Promise<ComparisonResult> {
  // Use mock data directly instead of API calls
  return new Promise((resolve) => {
    setTimeout(() => {
      // Get companies from mock data
      const companies = companyIds
        .map(id => mockCompanies[id])
        .filter(company => company !== undefined) as CompanyInfo[];
      
      // Create metrics object
      const metrics: ComparisonResult['metrics'] = {
        employees: {},
        founded: {},
        revenue: {}
      };
      
      // Populate metrics
      companies.forEach(company => {
        metrics.employees[company.id] = company.employees;
        metrics.founded[company.id] = company.founded;
        if (company.revenue) {
          metrics.revenue[company.id] = company.revenue;
        }
      });
      
      resolve({
        companies,
        metrics,
        timestamp: new Date()
      });
    }, 500); // Simulate network delay
  });
}