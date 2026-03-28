import React, { useEffect, useRef, useMemo } from 'react';
import Plotly from 'plotly.js-dist-min';

export default function PlotlyChart() {
  const chartRef = useRef(null);

  const { x, y, z } = useMemo(() => {
    const N = 50;
    const xs = Array.from({ length: N }, () => Math.random() * 100);
    const ys = Array.from({ length: N }, () => Math.floor(Math.random() * 120000) + 30000);
    const zs = xs.map((val, i) => {
      const incomeFactor = (120000 - ys[i]) / 120000;
      return Math.min(100, (val * 0.7) + (incomeFactor * 30) + (Math.random() * 10));
    });
    return { x: xs, y: ys, z: zs };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    const data = [{
      x: x, y: y, z: z,
      mode: 'markers',
      type: 'scatter3d',
      marker: {
        size: 4,
        color: z,
        colorscale: 'Viridis',
        opacity: 0.8,
        line: { color: 'rgba(255,255,255,0.1)', width: 0.5 }
      },
      hovertemplate: 'Risk: %{z:.1f}%<extra></extra>'
    }];

    const layout = {
      autosize: true,
      height: 380,
      margin: { l: 0, r: 0, b: 0, t: 0 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      scene: {
        xaxis: { title: 'Stress', gridcolor: 'rgba(255,255,255,0.05)', titlefont: { color: '#64748b' } },
        yaxis: { title: 'Income', gridcolor: 'rgba(255,255,255,0.05)', titlefont: { color: '#64748b' } },
        zaxis: { title: 'Risk %', gridcolor: 'rgba(255,255,255,0.05)', titlefont: { color: '#64748b' } },
        camera: { eye: { x: 1.5, y: 1.5, z: 1.2 } }
      },
      font: { family: 'Inter, sans-serif' }
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot(chartRef.current, data, layout, config);

    const handleResize = () => Plotly.Plots.resize(chartRef.current);
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) Plotly.purge(chartRef.current);
    };
  }, [x, y, z]);

  return (
    <div className="bg-slate-900/40 backdrop-blur-xl rounded-2xl border border-white/10 p-5 shadow-2xl h-full flex flex-col">
      <div className="flex justify-between items-center mb-4 px-1">
        <div>
          <h3 className="text-sm font-black text-white uppercase tracking-widest">AI Multi-Dimensional Risk Space</h3>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-tight mt-1">Multi-Signal Intelligence Mapping</p>
        </div>
        <div className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded text-[9px] font-black border border-cyan-500/20 uppercase">
          Live Plotly Engine
        </div>
      </div>
      
      <div className="flex-1 w-full min-h-[350px]" ref={chartRef}></div>
      
      <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/5 border-l-2 border-l-cyan-500">
        <p className="text-[11px] text-slate-400 leading-relaxed">
          <span className="text-cyan-400 font-bold">Mentor Note:</span> This 3D space maps non-linear behavioral clusters. Interact with the plot to explore high-risk density zones.
        </p>
      </div>
    </div>
  );
}
