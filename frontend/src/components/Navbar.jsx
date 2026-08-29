import React from 'react';
import { Database, Search, Award, FileText, Cpu } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, healthInfo }) {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Enterprise Multi-Vector Hybrid RAG
              </h1>
              <div className="flex items-center space-x-2 text-xs text-slate-400">
                <span className="flex items-center text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
                  RRF (k=60)
                </span>
                <span>•</span>
                <span>Context Engineering Engine</span>
              </div>
            </div>
          </div>

          <nav className="flex space-x-2 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'documents' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Documents ({healthInfo?.documents_count ?? 0})</span>
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'search' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Search className="w-4 h-4" />
              <span>RAG Hybrid Search</span>
            </button>
            <button
              onClick={() => setActiveTab('evaluation')}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'evaluation' ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Award className="w-4 h-4" />
              <span>Ragas Benchmarks</span>
            </button>
          </nav>

          <div className="hidden lg:flex items-center space-x-2 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50 text-xs">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-300 font-mono">{healthInfo?.database ? healthInfo.database.split(' ')[0] : 'Database Active'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
