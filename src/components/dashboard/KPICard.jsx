export default function KPICard({ 
  title, 
  value, 
  trend, 
  trendLabel, 
  icon: Icon, 
  trendUpIsGood = true,
  valueColor,
  secondaryLabel,
  tooltip,
  progressValue,
  progressColor
}) {
  const isUp = trend > 0;
  const isGood = isUp === trendUpIsGood;

  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 relative overflow-hidden group hover:border-cyan-500/30 transition-colors">
      <div className="absolute -right-4 -top-4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl group-hover:bg-cyan-500/20 transition-all"></div>
      
      <div className="flex justify-between items-start mb-4 relative">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-slate-400 text-sm font-medium">{title}</p>
            {tooltip && (
              <div className="relative flex items-center group/tooltip">
                <span className="text-slate-500 hover:text-cyan-400 cursor-help transition-colors text-xs font-bold border border-slate-600 rounded-full w-4 h-4 flex items-center justify-center">i</span>
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-slate-800 text-xs text-slate-300 rounded shadow-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all border border-slate-700 z-20 text-center">
                  {tooltip}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-700"></div>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <h3 className={`text-3xl font-bold tracking-tight ${valueColor || 'text-white'}`}>{value}</h3>
            {secondaryLabel && (
              <span className={`text-sm font-semibold ${valueColor || 'text-slate-400'}`}>{secondaryLabel}</span>
            )}
          </div>
        </div>
        <div className="w-12 h-12 rounded-xl bg-slate-800/80 flex items-center justify-center border border-slate-700/50 shrink-0 ml-2">
          <Icon className="w-6 h-6 text-cyan-400" />
        </div>
      </div>

      {progressValue !== undefined && (
        <div className="w-full h-1.5 bg-slate-800 rounded-full mb-3 overflow-hidden">
          <div className={`h-full ${progressColor || 'bg-cyan-500'} transition-all duration-1000`} style={{ width: `${progressValue}%` }}></div>
        </div>
      )}

      <div className="flex items-center gap-2 text-sm">
        <span className={`flex items-center font-medium ${isGood ? 'text-emerald-400' : 'text-rose-400'}`}>
          {isUp ? '↑' : '↓'} {Math.abs(trend)}%
        </span>
        <span className="text-slate-500">{trendLabel}</span>
      </div>
    </div>
  );
}
