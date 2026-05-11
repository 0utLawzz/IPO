"use client";

import { useState } from "react";
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
} from "lucide-react";

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

// Mock data for table
const MOCK_DATA = [
  { appNo: "TM-2024-001", class: "45", applicant: "ABC Enterprises", status: "Pending", date: "2024-01-15", office: "Karachi" },
  { appNo: "TM-2024-002", class: "35", applicant: "XYZ Corp", status: "Approved", date: "2024-02-20", office: "Lahore" },
  { appNo: "TM-2024-003", class: "42", applicant: "Tech Solutions", status: "Pending", date: "2024-03-10", office: "Islamabad" },
  { appNo: "TM-2024-004", class: "9", applicant: "Digital Systems", status: "Rejected", date: "2024-01-25", office: "Karachi" },
  { appNo: "TM-2024-005", class: "25", applicant: "Fashion Hub", status: "Approved", date: "2024-04-05", office: "Lahore" },
];

const STATS = [
  { label: "Total Applications", value: "1,247", change: "+12.5%", icon: Briefcase, color: "bg-primary" },
  { label: "Pending Review", value: "328", change: "+5.2%", icon: Clock, color: "bg-amber-500" },
  { label: "Approved This Month", value: "89", change: "+23.1%", icon: CheckCircle2, color: "bg-accent" },
  { label: "Success Rate", value: "78.4%", change: "+2.1%", icon: TrendingUp, color: "bg-blue-500" },
];

export default function Dashboard() {
  const [selectedTM, setSelectedTM] = useState("TM-01");
  const [searchQuery, setSearchQuery] = useState("");

  const selectedForm = TM_FORMS.find((f) => f.id === selectedTM);

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
                  {MOCK_DATA.map((row, index) => (
                    <tr key={index} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-foreground">{row.appNo}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.class}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.applicant}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                            row.status === "Approved"
                              ? "bg-green-100 text-green-700"
                              : row.status === "Pending"
                              ? "bg-amber-100 text-amber-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.date}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{row.office}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-border flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing <span className="font-medium">1</span> to <span className="font-medium">5</span> of{" "}
                <span className="font-medium">247</span> results
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
