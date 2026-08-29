import React, { useState } from 'react';
import { Search, Sparkles, BookOpen, Layers, AlertCircle, Clock } from 'lucide-react';
import { executeQuery } from '../api';
import RRFScoreBreakdown from './RRFScoreBreakdown';

export default function QuerySearch() {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState('HYBRID_RRF');
  const [topK, setTopK] = useState(10);
  const [topN, setTopN] = useState(5);
  const [rrfK, setRrfK] = useState(60);
  const [rerankThreshold, setRerankThreshold] = useState(0.3);

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [showBreakdown, setShowBreakdown] = useState(false);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await executeQuery({
        query: query.trim(),
        search_mode: searchMode,
        top_k: parseInt(topK),
        top_n: parseInt(topN),
        rrf_k: parseInt(rrfK),
        rerank_threshold: parseFloat(rerankThreshold)
      });
      setResponse(res);
    } catch (err) {
      setError(err.message || 'Search execution failed');
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    "Show me the year-over-year operational cash flow changes for subsidiary X.",
    "Dosage requirements of patient profile showing contraindications to drug Y.",
    "Which environmental sustainability reporting protocols are missing from our draft report?"
  ];

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
        <h2 className="text-lg font-semibold text-white mb-2 flex items-center space-x-2">
          <Search className="w-5 h-5 text-blue-400" />
          <span>Dual-Path Hybrid RAG Retrieval & QA Console</span>
        </h2>
        <p className="text-xs text-slate-400 mb-6">
          Combines dense semantic vectors (pgvector / Gemini embeddings) and sparse BM25 keyword matching via Reciprocal Rank Fusion (RRF).
        </p>

        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about uploaded enterprise documents..."
              className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white font-medium px-6 py-3 rounded-xl text-sm flex items-center space-x-2 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Searching...' : 'Execute Search'}</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2 items-center text-xs">
            <span className="text-slate-500 font-medium font-sans">Try domain prompts:</span>
            {sampleQueries.map((prompt, idx) => (
              <button key={idx} type="button" onClick={() => setQuery(prompt)} className="bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-lg truncate max-w-xs">
                {prompt}
              </button>
            ))}
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Retrieval Mode</label>
              <select value={searchMode} onChange={(e) => setSearchMode(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                <option value="HYBRID_RRF">Dual-Path Hybrid (RRF)</option>
                <option value="VECTOR_ONLY">Dense Vector Only</option>
                <option value="LEXICAL_ONLY">Sparse BM25 Only</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Candidate Top-K</label>
              <input type="number" value={topK} onChange={(e) => setTopK(e.target.value)} min="1" max="50" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 font-mono" />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Final Context Top-N</label>
              <input type="number" value={topN} onChange={(e) => setTopN(e.target.value)} min="1" max="20" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 font-mono" />
            </div>
            <div>
              <label className="block text-slate-400 mb-1 font-medium">RRF k Parameter</label>
              <input type="number" value={rrfK} onChange={(e) => setRrfK(e.target.value)} min="1" max="200" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 font-mono" />
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-4 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl p-3 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {response && (
        <div className="space-y-6">
          <div className="bg-slate-800/40 border border-blue-500/30 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-semibold text-white">Grounded GenAI Answer</h3>
              </div>
              <div className="flex items-center space-x-3 text-xs">
                <span className="text-slate-400 flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  <span className="font-mono">{response.execution_time_ms} ms</span>
                </span>
                <button onClick={() => setShowBreakdown(true)} className="bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 px-3 py-1 rounded-lg font-medium flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  <span>View RRF Breakdown</span>
                </button>
              </div>
            </div>

            <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed whitespace-pre-line mb-6">
              {response.answer}
            </div>

            {response.citations && response.citations.length > 0 && (
              <div className="bg-slate-950/70 rounded-xl p-4 border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center space-x-1.5">
                  <BookOpen className="w-4 h-4 text-blue-400" />
                  <span>Verified Source Citations ({response.citations.length})</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {response.citations.map((c) => (
                    <div key={c.citation_id} className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-xs">
                      <div className="flex items-center justify-between font-semibold text-blue-300 mb-1">
                        <span>Citation [{c.citation_id}]</span>
                        <span className="text-[11px] text-slate-400 font-normal">{c.filename} (Page {c.page_number})</span>
                      </div>
                      <p className="text-slate-400 text-[11px] italic line-clamp-2">"{c.snippet}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Top Reranked Context Chunks Injected to LLM ({response.retrieved_chunks.length})</span>
            </h3>

            <div className="space-y-4">
              {response.retrieved_chunks.map((chunk, idx) => (
                <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between text-slate-400 border-b border-slate-900 pb-2">
                    <span className="font-semibold text-slate-200">#{idx + 1} — {chunk.filename} (Page {chunk.metadata?.page_number ?? 1})</span>
                    <div className="flex space-x-3 font-mono text-[11px]">
                      <span className="text-cyan-400">Vec Rank: #{chunk.vector_rank ?? 'N/A'}</span>
                      <span className="text-amber-400">BM25 Rank: #{chunk.lexical_rank ?? 'N/A'}</span>
                      <span className="text-emerald-400 font-bold">RRF: {chunk.rrf_score?.toFixed(5)}</span>
                      <span className="text-indigo-400 font-bold">Rerank: {chunk.rerank_score?.toFixed(4)}</span>
                    </div>
                  </div>
                  <p className="text-slate-300 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">{chunk.raw_content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <RRFScoreBreakdown isOpen={showBreakdown} onClose={() => setShowBreakdown(false)} queryResponse={response} />
    </div>
  );
}
