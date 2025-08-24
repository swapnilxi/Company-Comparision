# Company Comparison Table Feature

## Overview

I've enhanced the company comparison functionality by adding a new **Comparison Table** feature that allows users to:

1. **Select companies** from the comparable companies list
2. **Compare parameters** in a well-formatted table
3. **Include/exclude the target company** in the comparison
4. **Fetch detailed financial data** for selected companies
5. **View comprehensive financial metrics** including ratios and performance indicators

## New Components

### 1. CompanyComparisonTable.tsx

A new React component that provides:

- **Interactive company selection** with checkboxes
- **Tabbed interface** to switch between Results View and Comparison Table
- **Comprehensive comparison table** with multiple parameters
- **Detailed financial metrics** when available
- **Responsive design** that works on all screen sizes

### 2. Enhanced Backend Endpoint

Added a new endpoint `/api/detailed-comparison` that provides:

- **Comprehensive financial data** for multiple companies
- **Financial ratios** (ROE, ROA, Debt-to-Equity, etc.)
- **Market data** and valuation metrics
- **Company profiles** and basic information

## Features

### Company Selection

- **Checkbox-based selection** for easy company picking
- **Select All/Clear** buttons for bulk operations
- **Auto-selection** of first 3 companies for better UX
- **Visual feedback** with highlighted selected companies

### Comparison Table

The table includes the following parameters:

#### Basic Information

- Company Name
- Ticker Symbol
- Website (clickable links)
- Description/Rationale

#### Financial Metrics (when available)

- Market Cap
- Revenue
- EBITDA
- P/E Ratio

#### Detailed Financial Ratios (with "Get Detailed Data" button)

- Return on Equity (ROE)
- Return on Assets (ROA)
- Debt to Equity Ratio
- Current Ratio
- Price to Book Ratio

### Target Company Integration

- **Toggle option** to include/exclude target company
- **Highlighted rows** for target company in the table
- **Seamless integration** with existing comparable companies

### Enhanced Data Fetching

- **"Get Detailed Data" button** for additional financial metrics
- **Loading states** and error handling
- **Comprehensive financial ratios** from FMP API
- **Real-time data** for accurate comparisons

## Usage

1. **Search for companies** using any of the existing methods (ticker, name, website)
2. **View results** in the default Results View tab
3. **Switch to Comparison Table** tab to see the new comparison interface
4. **Select companies** you want to compare using the checkboxes
5. **Optionally include target company** in the comparison
6. **Click "Get Detailed Data"** to fetch additional financial metrics
7. **Compare parameters** in the comprehensive table format

## Technical Implementation

### Frontend

- **TypeScript** for type safety
- **React hooks** for state management
- **Tailwind CSS** for styling
- **Responsive design** with mobile support

### Backend

- **FastAPI** endpoint for detailed comparison data
- **FMP API integration** for financial metrics
- **Error handling** and validation
- **Rate limiting** considerations

### Data Flow

1. User selects companies in the frontend
2. Frontend calls `/api/detailed-comparison` endpoint
3. Backend fetches data from FMP API for each ticker
4. Data is processed and formatted
5. Frontend displays the comparison table

## Benefits

1. **Better User Experience**: Easy-to-use interface for company comparison
2. **Comprehensive Data**: Access to detailed financial metrics
3. **Flexible Selection**: Users can choose which companies to compare
4. **Visual Clarity**: Well-formatted table makes comparisons easy
5. **Extensible**: Easy to add more metrics and parameters

## Future Enhancements

Potential improvements could include:

- **Export functionality** (PDF, Excel)
- **Chart visualizations** for metrics
- **Custom metric calculations**
- **Historical data comparison**
- **Industry benchmarking**
- **Screening and filtering options**
