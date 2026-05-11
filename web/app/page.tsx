"use client";

import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  FileText,
  Settings,
  Search,
  Calendar,
  Download,
  ChevronDown,
  Filter,
  MoreHorizontal,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  Users,
  Briefcase,
  Loader2,
} from "lucide-react";
import { fetchSheetData, parseSheetData, calculateStats, formatRowData } from "@/lib/sheets";

// TM Forms data matching config.py
const TM_FORMS = [
  { id: "TM-01", name: "TM 01", description: "Application for registration", fee: 3000, check: "COL H", enabled: true },
  { id: "TM-02", name: "TM 02", description: "Registration from Convention Country", fee: 3000, check: "NO CHECK", enabled: true },
  { id: "TM-05", name: "TM 05", description: "Notice of Opposition", fee: 9000, check: "COL B", enabled: true },
  { id: "TM-06", name: "TM 06", description: "Form of Counter-statement", fee: 1500, check: "COL B", enabled: true },
  { id: "TM-07", name: "TM 07", description: "Notice to attend hearing", fee: 600, check: "NO CHECK", enabled: true },
  { id: "TM-11", name: "TM 11", description: "One registration of trademark", fee: 9000, check: "COL C", enabled: true },
  { id: "TM-12", name: "TM 12", description: "Renewal of registration", fee: 15000, check: "COL B", enabled: true },
  { id: "TM-13", name: "TM 13", description: "Request for restoration", fee: 3000, check: "COL B", enabled: true },
  { id: "TM-15", name: "TM 15", description: "Request grounds of decision", fee: 1500, check: "COL B", enabled: true },
  { id: "TM-16", name: "TM 16", description: "Correction/amendment", fee: 600, check: "COL C", enabled: true },
  { id: "TM-24", name: "TM 24", description: "Register subsequent proprietor", fee: "6000 / 7500", check: "COL B", enabled: true },
  { id: "TM-33", name: "TM 33", description: "Change name/description", fee: 1500, check: "COL B", enabled: true },
  { id: "TM-34", name: "TM 34", description: "Alter address entries", fee: 600, check: "COL B", enabled: true },
  { id: "TM-46", name: "TM 46", description: "Request certificate", fee: 1500, check: "COL B", enabled: true },
  { id: "TM-55", name: "TM 55", description: "Request for search", fee: 1000, check: "NO CHECK", enabled: true },
  { id: "TM-56", name: "TM 56", description: "Extension of time", fee: 1500, check: "COL B", enabled: true },
  { id: "TM-57", name: "TM 57", description: "Restoration abandoned mark", fee: 1500, check: "COL C", enabled: true },
];

interface TableRow {
  appNo: string;
  class: string;
  applicant: string;
  status: string;
  date: string;
  office: string;
}

export default function Dashboard() {
  const [selectedTM, setSelectedTM] = useState("TM-01");
  const [searchQuery, setSearchQuery] = useState("");
  const [data, setData] = useState<TableRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    successRate: '0.0'
  });

  const selectedForm = TM_FORMS.find((f) => f.id === selectedTM);

  // Fetch data when selected TM changes
  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const sheetName = selectedForm?.id || 'TM-01';
        const values = await fetchSheetData(sheetName);
        const { rows } = parseSheetData(values);
        const formattedData = rows.map(formatRowData);
        setData(formattedData);
        
        // Calculate stats
        const calculatedStats = calculateStats(rows);
        setStats(calculatedStats);
      } catch (err) {
        console.error('Failed to fetch sheet data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setData([]);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [selectedTM, selectedForm]);

  // Filter data based on search query
  const filteredData = data.filter(row =>
    row.appNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
    row.applicant.toLowerCase().includes(searchQuery.toLowerCase()) ||
    row.class.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Generate stats cards dynamically
  const STATS = [
    { 
      label: "Total Applications", 
      value: stats.total.toLocaleString(), 
      change: "+", 
      icon: Briefcase, 
      color: "bg-primary" 
    },
    { 
      label: "Pending Review", 
      value: stats.pending.toLocaleString(), 
      change: "+", 
      icon: Clock, 
      color: "bg-amber-500" 
    },
    { 
      label: "Approved", 
      value: stats.approved.toLocaleString(), 
      change: "+", 
      icon: CheckCircle2, 
      color: "bg-accent" 
    },
    { 
      label: "Success Rate", 
      value: `${stats.successRate}%`, 
      change: "+", 
      icon: TrendingUp, 
      color: "bg-blue-500" 
    },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <span className="text-white font-bold text-lg">IP</span>
            </div>
            <div>
              <h1 className="font-bold text-foreground text-lg">IPO Pakistan</h1>
              <p className="text-xs text-muted-foreground">Trademark Dashboard</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            General
          </div>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-primary/10 text-primary font-medium">
            <LayoutDashboard className="w-5 h-5" />
            Dashboard
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:bg-muted/50 transition-colors">
            <FileText className="w-5 h-5" />
            Submissions
          </button>

          <div className="mt-6 px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            TM Forms
          </div>
          <div className="space-y-1">
            {TM_FORMS.filter((f) => f.enabled).map((form) => (
              <button
                key={form.id}
                onClick={() => setSelectedTM(form.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedTM === form.id
                    ? "bg-primary text-white"
                    : "text-muted-foreground hover:bg-muted/50"
                }`}
              >
                <span className="font-medium">{form.name}</span>
                {form.check !== "NO CHECK" && (
                  <span className={`text-xs px-1.5 py-0.5 rounded ${selectedTM === form.id ? "bg-white/20" : "bg-primary/10 text-primary"}`}>
                    {form.check}
                  </span>
                )}
              </button>
            ))}
          </div>
        </nav>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-border space-y-1">
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:bg-muted/50 transition-colors">
            <Settings className="w-5 h-5" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search applications..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border bg-card hover:bg-muted/50 transition-colors text-sm">
              <Calendar className="w-4 h-4" />
              <span>Last 30 days</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark transition-colors text-sm font-medium">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto p-6">
          {/* Selected TM Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-foreground">{selectedForm?.name}</h2>
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                PKR {selectedForm?.fee.toLocaleString()}
              </span>
            </div>
            <p className="text-muted-foreground">{selectedForm?.description}</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {STATS.map((stat, index) => (
              <div key={index} className="bg-card rounded-xl p-5 border border-border shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-10 h-10 rounded-lg ${stat.color} flex items-center justify-center`}>
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs font-medium text-accent flex items-center gap-1">
                    {stat.change}
                    <TrendingUp className="w-3 h-3" />
                  </span>
                </div>
                <div className="text-2xl font-bold text-foreground mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Data Table */}
          <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <h3 className="font-semibold text-foreground">Recent Applications</h3>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:bg-muted/50 transition-colors">
                  <Filter className="w-4 h-4" />
                  Filter
                </button>
                <button className="p-1.5 rounded-lg text-muted-foreground hover:bg-muted/50 transition-colors">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted/50">
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Application No
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Class
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Applicant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Office
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {loading && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary mb-2" />
                        <p className="text-muted-foreground">Loading data from Google Sheets...</p>
                      </td>
                    </tr>
                  )}
                  {error && !loading && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center">
                        <AlertCircle className="w-8 h-8 mx-auto text-red-500 mb-2" />
                        <p className="text-red-500 font-medium mb-1">Failed to load data</p>
                        <p className="text-sm text-muted-foreground">{error}</p>
                        <p className="text-xs text-muted-foreground mt-2">
                          Make sure NEXT_PUBLIC_GOOGLE_API_KEY is configured in Vercel
                        </p>
                      </td>
                    </tr>
                  )}
                  {!loading && !error && filteredData.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-muted-foreground">
                        No data found{searchQuery ? ' for this search' : ''}
                      </td>
                    </tr>
                  )}
                  {!loading && !error && filteredData.map((row, index) => (
                    <tr key={index} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-foreground">{row.appNo || '-'}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.class || '-'}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.applicant || '-'}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                            row.status?.toLowerCase().includes('approved') || row.status?.toLowerCase().includes('accepted')
                              ? "bg-green-100 text-green-700"
                              : row.status?.toLowerCase().includes('pending')
                              ? "bg-amber-100 text-amber-700"
                              : row.status?.toLowerCase().includes('reject') || row.status?.toLowerCase().includes('refused')
                              ? "bg-red-100 text-red-700"
                              : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {row.status || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.date || '-'}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.office || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-border flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing <span className="font-medium">{loading ? 0 : 1}</span> to <span className="font-medium">{loading ? 0 : filteredData.length}</span> of{" "}
                <span className="font-medium">{stats.total}</span> results
              </div>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:bg-muted/50 transition-colors disabled:opacity-50" disabled>
                  Previous
                </button>
                <button className="px-3 py-1.5 rounded-lg border border-border text-sm text-muted-foreground hover:bg-muted/50 transition-colors">
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
