import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DocumentUploader from './components/DocumentUploader';
import DocumentList from './components/DocumentList';
import QuerySearch from './components/QuerySearch';
import EvaluationPanel from './components/EvaluationPanel';
import { checkHealth, listDocuments } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [healthInfo, setHealthInfo] = useState(null);
  const [documents, setDocuments] = useState([]);

  const loadHealth = async () => {
    try {
      const data = await checkHealth();
      setHealthInfo(data);
    } catch (e) {
      console.error('Health check failed:', e);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (e) {
      console.error('Failed to load documents:', e);
    }
  };

  useEffect(() => {
    loadHealth();
    loadDocuments();
  }, []);

  const handleDocumentProcessed = () => {
    loadHealth();
    loadDocuments();
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col selection:bg-blue-500 selection:text-white">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} healthInfo={healthInfo} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'documents' && (
          <div className="space-y-6">
            <DocumentUploader onDocumentProcessed={handleDocumentProcessed} />
            <DocumentList documents={documents} onRefresh={loadDocuments} />
          </div>
        )}
        {activeTab === 'search' && <QuerySearch />}
        {activeTab === 'evaluation' && <EvaluationPanel />}
      </main>
      <footer className="border-t border-slate-800 bg-slate-950/60 py-4 text-center text-xs text-slate-500">
        Enterprise Multi-Vector Hybrid RAG Search Engine • Built with FastAPI, Reciprocal Rank Fusion, pgvector & Gemini 2.5
      </footer>
    </div>
  );
}
