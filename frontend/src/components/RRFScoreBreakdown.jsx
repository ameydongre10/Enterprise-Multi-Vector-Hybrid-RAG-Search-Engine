import React from 'react';
import { Layers, Zap } from 'lucide-react';

export default function RRFScoreBreakdown({ isOpen, onClose, queryResponse }) {
  if (!isOpen || !queryResponse) return null;
  const { retrieved_chunks, rrf_stats, query } = queryResponse;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full p-6 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex justify-between items-center pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Layers className="w-5 h-5 text-blue-400" />
              <span>Reciprocal Rank Fusion (RRF) & Rerank Breakdown</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Query: <span className="text-indigo-300 font-mono">"{query}"</span> | Formula: <span className="font-mono text-cyan-400">RRF_Score = 1/(k + VectorRank) + 1/(k + BM25Rank)</span> (k={rrf_stats?.rrf_k ?? 60})
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-lg font-bold">✕</button>
        </div>

        <div className="overflow-y-auto my-4 flex-1">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 font-mono border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Chunk ID</th>
                <th className="py-2.5 px-3">Document Source</th>
                <th className="py-2.5 px-3 text-center">Vector Sim Score</th>
                <th className="py-2.5 px-3 text-center">Vector Rank</th>
                <th className="py-2.5 px-3 text-center">BM25 Score</th>
                <th className="py-2.5 px-3 text-center">BM25 Rank</th>
                <th className="py-2.5 px-3 text-center">Aggregate RRF Score</th>
                <th className="py-2.5 px-3 text-center">Cross-Encoder Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {retrieved_chunks.map((chunk, idx) => (
                <tr key={idx} className="hover:bg-slate-800/50">
                  <td className="py-3 px-3 text-blue-400 font-semibold">{chunk.chunk_id.slice(0, 8)}...</td>
                  <td className="py-3 px-3 text-slate-200">{chunk.filename} (p.{chunk.metadata?.page_number ?? 1})</td>
                  <td className="py-3 px-3 text-center text-cyan-300">{chunk.vector_score !== null ? chunk.vector_score.toFixed(4) : '-'}</td>
                  <td className="py-3 px-3 text-center text-slate-400">{chunk.vector_rank ? `#${chunk.vector_rank}` : '-'}</td>
                  <td className="py-3 px-3 text-center text-amber-300">{chunk.lexical_score !== null ? chunk.lexical_score.toFixed(2) : '-'}</td>
                  <td className="py-3 px-3 text-center text-slate-400">{chunk.lexical_rank ? `#${chunk.lexical_rank}` : '-'}</td>
                  <td className="py-3 px-3 text-center text-emerald-400 font-bold bg-emerald-500/10 rounded">{chunk.rrf_score?.toFixed(6)}</td>
                  <td className="py-3 px-3 text-center text-indigo-400 font-bold">{chunk.rerank_score?.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span className="flex items-center space-x-1.5 text-slate-300">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Dual-path retrieval eliminated vector-only blindspots for keyword-exact and semantic queries.</span>
          </span>
          <button onClick={onClose} className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg text-xs">Close Breakdown</button>
        </div>
      </div>
    </div>
  );
}
