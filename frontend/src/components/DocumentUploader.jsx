import React, { useState, useRef } from 'react';
import { UploadCloud, File, Loader2, AlertCircle } from 'lucide-react';
import { uploadDocument, getTaskStatus } from '../api';

export default function DocumentUploader({ onDocumentProcessed }) {
  const [isDragging, setIsDragging] = useState(false);
  const [activeTask, setActiveTask] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (file) => {
    if (!file) return;
    setError(null);
    setActiveTask({ task_id: 'pending', status: 'UPLOADING', progress: 5, message: `Uploading ${file.name}...` });

    try {
      const res = await uploadDocument(file);
      setActiveTask(res);
      pollTaskStatus(res.task_id);
    } catch (err) {
      setError(err.message || 'Upload failed');
      setActiveTask(null);
    }
  };

  const pollTaskStatus = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const statusRes = await getTaskStatus(taskId);
        setActiveTask(statusRes);

        if (statusRes.status === 'COMPLETED') {
          clearInterval(interval);
          setTimeout(() => {
            setActiveTask(null);
            if (onDocumentProcessed) onDocumentProcessed();
          }, 1500);
        } else if (statusRes.status === 'FAILED') {
          clearInterval(interval);
          setError(statusRes.error || 'Ingestion pipeline failed');
        }
      } catch (e) {
        clearInterval(interval);
        setError('Error tracking task status');
      }
    }, 1000);
  };

  return (
    <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <h2 className="text-lg font-semibold text-white mb-2 flex items-center space-x-2">
        <UploadCloud className="w-5 h-5 text-blue-400" />
        <span>Document Ingestion Hub</span>
      </h2>
      <p className="text-xs text-slate-400 mb-4">
        Supports PDF (Layout/Tables), DOCX, CSV, TSV, and TXT. Executes contextualized parent-child chunking & global summarization.
      </p>

      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragging ? 'border-blue-500 bg-blue-500/10 scale-[1.01]' : 'border-slate-700 hover:border-slate-500 bg-slate-900/40 hover:bg-slate-900/60'
        }`}
      >
        <input ref={fileInputRef} type="file" accept=".pdf,.docx,.doc,.csv,.tsv,.xlsx,.txt,.md" className="hidden" onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])} />
        <div className="w-12 h-12 mx-auto rounded-full bg-blue-600/10 text-blue-400 flex items-center justify-center mb-3">
          <File className="w-6 h-6" />
        </div>
        <p className="text-sm font-medium text-slate-200">Click to upload or drag & drop files here</p>
        <p className="text-xs text-slate-500 mt-1">PDF, DOCX, CSV, TXT (up to 100MB)</p>
      </div>

      {activeTask && (
        <div className="mt-4 bg-slate-900/80 border border-blue-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="font-medium text-blue-400 flex items-center space-x-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>{activeTask.status}: {activeTask.message}</span>
            </span>
            <span className="font-mono text-slate-300">{activeTask.progress}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 h-2 transition-all duration-300 rounded-full" style={{ width: `${activeTask.progress}%` }} />
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl p-3 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
