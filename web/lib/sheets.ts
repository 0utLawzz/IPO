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
export function parseSheetData(values: string[][]): { headers: string[]; rows: Record<string, string>[] } {
  if (!values || values.length === 0) {
    return { headers: [], rows: [] };
  }
  
  const headers = values[0];
  const rows = values.slice(1).map((row) => {
    const rowData: Record<string, string> = {};
    headers.forEach((header, index) => {
      rowData[header] = row[index] || '';
    });
    return rowData;
  });
  
  return { headers, rows };
}

// Calculate stats from sheet data
export function calculateStats(rows: Record<string, string>[]) {
  const total = rows.length;
  
  // Count by status - look for common status column names
  const pending = rows.filter(r => 
    r['Status']?.toLowerCase().includes('pending') ||
    r['status']?.toLowerCase().includes('pending') ||
    r['Application Status']?.toLowerCase().includes('pending')
  ).length;
  
  const approved = rows.filter(r => 
    r['Status']?.toLowerCase().includes('approved') ||
    r['status']?.toLowerCase().includes('approved') ||
    r['Application Status']?.toLowerCase().includes('approved') ||
    r['Status']?.toLowerCase().includes('accepted') ||
    r['status']?.toLowerCase().includes('accepted')
  ).length;
  
  const rejected = rows.filter(r => 
    r['Status']?.toLowerCase().includes('reject') ||
    r['status']?.toLowerCase().includes('reject') ||
    r['Application Status']?.toLowerCase().includes('reject') ||
    r['Status']?.toLowerCase().includes('refused') ||
    r['status']?.toLowerCase().includes('refused')
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
export function formatRowData(row: Record<string, string>): {
  appNo: string;
  class: string;
  applicant: string;
  status: string;
  date: string;
  office: string;
} {
  // Try to find common column names
  const appNo = row['Application No'] || row['Application Number'] || row['appNo'] || row['TM No'] || '';
  const classVal = row['Class'] || row['class'] || row['Nice Class'] || '';
  const applicant = row['Applicant'] || row['applicant'] || row['Proprietor'] || row['Owner'] || '';
  const status = row['Status'] || row['status'] || row['Application Status'] || 'Unknown';
  const date = row['Date'] || row['Filing Date'] || row['date'] || '';
  const office = row['Office'] || row['Regional Office'] || row['office'] || 'Karachi';
  
  return {
    appNo,
    class: classVal,
    applicant,
    status,
    date,
    office
  };
}
