"use client";

import React from 'react';
import { CompanyInfo } from '../utils/companyUtils';
import { formatCurrency } from '../utils/helpers.js';

interface CompanyCardProps {
  company: CompanyInfo;
  highlighted?: boolean;
}

/**
 * Company information card component
 * Demonstrates using TypeScript interfaces with JavaScript utility functions
 */
const CompanyCard: React.FC<CompanyCardProps> = ({ company, highlighted = false }) => {
  const cardClasses = `
    p-6 rounded-lg shadow-md 
    ${highlighted ? 'bg-blue-50 border border-blue-200' : 'bg-white'}
  `;

  return (
    <div className={cardClasses}>
      <h3 className="text-xl font-bold mb-2">{company.name}</h3>
      <div className="text-sm text-gray-600 mb-4">{company.industry}</div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-xs text-gray-500">Founded</div>
          <div>{company.founded}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Employees</div>
          <div>{company.employees.toLocaleString()}</div>
        </div>
        {company.revenue && (
          <div className="col-span-2">
            <div className="text-xs text-gray-500">Annual Revenue</div>
            <div>{formatCurrency(company.revenue)}</div>
          </div>
        )}
      </div>
      
      {company.description && (
        <p className="text-sm text-gray-700">{company.description}</p>
      )}
    </div>
  );
};

export default CompanyCard;