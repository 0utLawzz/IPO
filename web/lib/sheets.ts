import { google } from 'googleapis';

const SHEET_ID = process.env.NEXT_PUBLIC_SHEET_ID || '1CLZSTLR17cSTo-ERZkpRc1HuXYQ93PZumxyQY5x0qZ4';

// For client-side, we use a simple fetch approach with a public API key
// or proxy through our own API endpoint
export async function fetchSheetData(sheetName: string): Promise<string[][]> {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_API_KEY;
  
  if (!apiKey) {
    throw new Error('Google API key not configured');
  }

  const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(sheetName)}?key=${apiKey}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch sheet data: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.values || [];
}

// Parse sheet data into structured format
// Handles IPO Pakistan sheet structure with flexible column mapping
export function parseSheetData(values: string[][]): { headers: string[]; rows: Record<string, string>[] } {
  if (!values || values.length === 0) {
    return { headers: [], rows: [] };
  }
  
  // Check if first row looks like headers (contains text like "Application", "TM", etc.)
  const firstRow = values[0];
  const hasHeaders = firstRow.some(cell => 
    /application|tm|no|number|class|date|status|applicant|proprietor|mark/i.test(cell)
  );
  
  let headers: string[];
  let dataRows: string[][];
  
  if (hasHeaders) {
    headers = firstRow.map((h, i) => h || `Column${i}`);
    dataRows = values.slice(1);
  } else {
    // No headers - create generic column names
    headers = firstRow.map((_, i) => `Column${i}`);
    dataRows = values;
  }
  
  const rows = dataRows.map((row) => {
    const rowData: Record<string, string> = {};
    headers.forEach((header, index) => {
      rowData[header] = row[index] || '';
    });
    // Also add index-based access for flexibility
    row.forEach((cell, index) => {
      rowData[`_${index}`] = cell || '';
    });
    return rowData;
  });
  
  return { headers, rows };
}

// Calculate stats from sheet data with flexible column detection
export function calculateStats(rows: Record<string, string>[]) {
  const total = rows.length;
  
  // Helper to check status in any possible column
  const getStatus = (r: Record<string, string>): string => {
    const possibleKeys = ['Status', 'status', 'Application Status', 'Stage', '_5', '_6', '_8', '_9'];
    for (const key of possibleKeys) {
      if (r[key]) return r[key].toLowerCase();
    }
    return '';
  };
  
  // Count by status
  const pending = rows.filter(r => 
    getStatus(r).includes('pending') || getStatus(r).includes('under examination')
  ).length;
  
  const approved = rows.filter(r => 
    getStatus(r).includes('approved') || 
    getStatus(r).includes('accepted') ||
    getStatus(r).includes('registered') ||
    getStatus(r).includes('granted')
  ).length;
  
  const rejected = rows.filter(r => 
    getStatus(r).includes('reject') || 
    getStatus(r).includes('refused') ||
    getStatus(r).includes('abandoned') ||
    getStatus(r).includes('withdrawn')
  ).length;
  
  const successRate = total > 0 ? ((approved / total) * 100).toFixed(1) : '0.0';
  
  return {
    total,
    pending,
    approved,
    rejected,
    successRate
  };
}

// Format row for display
// Uses column name matching with index-based fallback
export function formatRowData(row: Record<string, string>): {
  appNo: string;
  class: string;
  applicant: string;
  status: string;
  date: string;
  office: string;
} {
  // Helper to get value by trying multiple possible keys
  const getValue = (...keys: string[]): string => {
    for (const key of keys) {
      if (row[key] && row[key].trim()) return row[key].trim();
    }
    return '';
  };
  
  // Try named columns first, then fall back to index positions
  // Common IPO sheet structures: [0]=No, [1]=AppNo, [2]=Mark, [3]=Class, [4]=Proprietor, [5]=Status, [6]=Date
  const appNo = getValue('Application No', 'Application Number', 'appNo', 'TM No', 'Trademark No', '_1', '_0');
  const mark = getValue('Mark', 'Trade Mark', 'Trademark', 'Trade_Mark', '_2');
  const classVal = getValue('Class', 'class', 'Nice Class', 'Cl', '_3', '_4');
  const applicant = getValue('Proprietor', 'Applicant', 'applicant', 'Owner', 'Name', '_4', '_5', '_3');
  const status = getValue('Status', 'status', 'Application Status', 'Stage', '_5', '_6', '_8') || 'Unknown';
  const date = getValue('Date', 'Filing Date', 'date', 'Filing_Date', 'Registration Date', '_6', '_7');
  const office = getValue('Office', 'Regional Office', 'office', 'IPO Office', '_7', '_8', '_9') || 'Karachi';
  
  // Combine mark with appNo if available for better display
  const displayAppNo = appNo || mark || 'N/A';
  
  return {
    appNo: displayAppNo,
    class: classVal,
    applicant,
    status,
    date,
    office
  };
}
