import React, { useState, useEffect } from 'react';
import { Award, Play, ShieldCheck, BarChart2 } from 'lucide-react';
import { runEvaluation } from '../api';

export default function EvaluationPanel() {
  const [loading, setLoading] = useState(false);
  const [evalData, setEvalData] = useState(null);
  const [error, setError] = useState(null);

  const executeEval = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runEvaluation();
      setEvalData(data);
    } catch (err) {
      setError(err.message || 'Evaluation run failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeEval();
  }, []);

  return (
    <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
            <Award className="w-5 h-5 text-amber-400" />
            <span>Ragas Evaluation Framework & Quality Benchmarks</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Automated quality measurement suite evaluating faithfulness, answer relevance, context recall, and precision.</p>
        </div>
        <button onClick={executeEval} disabled={loading} className="bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 px-4 py-2 rounded-xl text-xs font-semibold flex items-center space-x-2 disabled:opacity-50">
          <Play className="w-3.5 h-3.5" />
          <span>{loading ? 'Running Benchmark...' : 'Run Ragas Evaluation'}</span>
        </button>
      </div>

      {evalData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {evalData.metrics.map((m, idx) => {
              const pct = (m.score * 100).toFixed(1);
              return (
                <div key={idx} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-xs text-slate-400 font-medium flex items-center justify-between">
                    <span>{m.metric_name}</span>
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-bold text-white font-mono flex items-baseline space-x-1">
                    <span>{pct}%</span>
                    <span className="text-xs text-slate-500 font-normal">({m.score})</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-1.5 rounded-full" style={{ width: `${pct}%` }} />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 leading-tight">{m.description}</p>
                </div>
              );
            })}
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-blue-400" />
              <span>Benchmark Test Set Breakdown ({evalData.sample_count} Samples)</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 text-slate-400 font-mono border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">Test Query</th>
                    <th className="py-2.5 px-3 text-center">Faithfulness</th>
                    <th className="py-2.5 px-3 text-center">Relevance</th>
                    <th className="py-2.5 px-3 text-center">Recall</th>
                    <th className="py-2.5 px-3 text-center">Precision</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-900 font-mono">
                  {evalData.details.map((item, i) => (
                    <tr key={i} className="hover:bg-slate-900/50">
                      <td className="py-2.5 px-3 text-slate-200">{item.query}</td>
                      <td className="py-2.5 px-3 text-center text-emerald-400 font-bold">{item.faithfulness}</td>
                      <td className="py-2.5 px-3 text-center text-cyan-400 font-bold">{item.answer_relevance}</td>
                      <td className="py-2.5 px-3 text-center text-indigo-400 font-bold">{item.context_recall}</td>
                      <td className="py-2.5 px-3 text-center text-amber-400 font-bold">{item.context_precision}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
