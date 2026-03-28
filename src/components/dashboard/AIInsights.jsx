import { Sparkles, AlertTriangle, TrendingUp, Info } from "lucide-react";

export default function AIInsights({ insights }) {
  const getIcon = (type) => {
    switch(type) {
      case 'alert': return <AlertTriangle className="w-5 h-5 text-amber-400" />;
      case 'trend': return <TrendingUp className="w-5 h-5 text-cyan-400" />;
      default: return <Info className="w-5 h-5 text-blue-400" />;
    }
  };

  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-6 border-b border-slate-700/50 pb-4">
        <Sparkles className="w-5 h-5 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">AI Insights</h3>
      </div>
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
        {insights.map((insight, idx) => (
          <div key={idx} className="flex gap-4 items-start p-4 rounded-xl bg-slate-800/30 border border-slate-700/30 hover:border-slate-600 transition-colors">
            <div className="mt-0.5">{getIcon(insight.type)}</div>
            <div>
              <p className="text-sm text-slate-200 leading-relaxed font-medium">{insight.message}</p>
              <span className="text-xs text-slate-500 mt-1.5 block">{insight.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
