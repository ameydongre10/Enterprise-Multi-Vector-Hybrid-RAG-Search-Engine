import React, { useState } from 'react';
import { FileText, Trash2, Info, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { deleteDocument } from '../api';

export default function DocumentList({ documents, onRefresh }) {
  const [selectedContext, setSelectedContext] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document and its vector chunks?')) return;
    setDeletingId(docId);
    try {
      await deleteDocument(docId);
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Delete failed: ' + e.message);
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3 h-3 mr-1" /> Ready</span>;
      case 'FAILED':
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20"><AlertTriangle className="w-3 h-3 mr-1" /> Failed</span>;
      default:
        return <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse"><Clock className="w-3 h-3 mr-1" /> {status}</span>;
    }
  };

  return (
    <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-sm mt-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <span>Indexed Document Knowledge Registry</span>
        </h2>
        <button onClick={onRefresh} className="text-xs text-blue-400 hover:text-blue-300 font-medium px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
          Refresh Registry
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 text-slate-500 text-sm border border-dashed border-slate-700/60 rounded-xl">
          No documents uploaded yet. Upload financial filings, clinical guides, legal contracts, or tabular CSVs above.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 font-medium uppercase tracking-wider border-b border-slate-700">
              <tr>
                <th className="py-3 px-4">Filename</th>
                <th className="py-3 px-4">Size</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Chunks</th>
                <th className="py-3 px-4">Global Context Header</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-medium text-white flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-blue-400 shrink-0" />
                    <span className="truncate max-w-[200px]">{doc.filename}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-mono">{(doc.file_size_bytes / 1024).toFixed(1)} KB</td>
                  <td className="py-3 px-4">{getStatusBadge(doc.processing_status)}</td>
                  <td className="py-3 px-4 font-mono text-indigo-300">{doc.chunk_count} chunks</td>
                  <td className="py-3 px-4 max-w-[300px]">
                    {doc.global_context ? (
                      <button onClick={() => setSelectedContext({ filename: doc.filename, context: doc.global_context })} className="text-left text-slate-400 hover:text-blue-300 truncate block w-full text-xs hover:underline">
                        {doc.global_context}
                      </button>
                    ) : <span className="text-slate-600 italic">Generating...</span>}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button onClick={() => handleDelete(doc.id)} disabled={deletingId === doc.id} className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedContext && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-4 border-b border-slate-800 pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span>Global Context Header — {selectedContext.filename}</span>
              </h3>
              <button onClick={() => setSelectedContext(null)} className="text-slate-400 hover:text-white text-sm">✕</button>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl text-xs text-slate-300 font-mono leading-relaxed border border-slate-800">{selectedContext.context}</div>
          </div>
        </div>
      )}
    </div>
  );
}
