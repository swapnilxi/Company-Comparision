/**
 * Analytics utilities using JSDoc for TypeScript type integration
 * This demonstrates how to use TypeScript types in JavaScript files
 * @module analytics
 */

// Import TypeScript types using JSDoc
/** @typedef {import('./companyUtils').CompanyInfo} CompanyInfo */
/** @typedef {import('./companyUtils').ComparisonResult} ComparisonResult */

/**
 * Track a company view event
 * @param {CompanyInfo} company - The company that was viewed
 * @param {string} source - The source of the view (search, recommendation, etc.)
 * @returns {void}
 */
export function trackCompanyView(company, source) {
  console.log(`Analytics: Company ${company.name} viewed from ${source}`);
  
  // In a real app, this would send data to an analytics service
  const eventData = {
    eventType: 'company_view',
    companyId: company.id,
    companyName: company.name,
    industry: company.industry,
    source: source,
    timestamp: new Date().toISOString()
  };
  
  // Mock analytics call
  setTimeout(() => {
    console.log('Analytics event sent:', eventData);
  }, 100);
}

/**
 * Track a comparison event
 * @param {ComparisonResult} comparisonResult - The result of a company comparison
 * @returns {Promise<boolean>} - Whether the event was tracked successfully
 */
export async function trackComparisonEvent(comparisonResult) {
  try {
    const companyIds = comparisonResult.companies.map(c => c.id);
    const metrics = Object.keys(comparisonResult.metrics);
    
    console.log(`Analytics: Comparison of ${companyIds.join(', ')} tracked`);
    console.log(`Metrics compared: ${metrics.join(', ')}`);
    
    // In a real app, this would send data to an analytics service
    return true;
  } catch (error) {
    console.error('Failed to track comparison event:', error);
    return false;
  }
}