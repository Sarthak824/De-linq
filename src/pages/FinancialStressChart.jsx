import PlotDefault from 'react-plotly.js';

// Handle Vite's CommonJS to ESM interop wrapper for react-plotly.js
const Plot = PlotDefault.default || PlotDefault;

export default function FinancialStressChart({ data }) {
  return (
    <div className="bg-slate-900/50 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold text-white mb-6">Financial Stress Trends</h3>
      <div className="flex-1 w-full min-h-[300px]">
        <Plot
          data={[
            {
              x: data.dates,
              y: data.stressLevels,
              type: 'scatter',
              mode: 'lines+markers',
              marker: { color: '#06b6d4' },
              line: { shape: 'spline', smoothing: 1.3, width: 3 },
              name: 'Stress Level',
              fill: 'tozeroy',
              fillcolor: 'rgba(6, 182, 212, 0.1)',
            }
          ]}
          layout={{
            autosize: true,
            margin: { t: 10, r: 10, l: 40, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#94a3b8' },
            xaxis: {
              showgrid: true,
              gridcolor: 'rgba(51, 65, 85, 0.5)',
              zeroline: false,
            },
            yaxis: {
              showgrid: true,
              gridcolor: 'rgba(51, 65, 85, 0.5)',
              zeroline: false,
            },
            legend: {
              orientation: 'h',
              y: -0.2,
            },
            hovermode: 'x unified'
          }}
          useResizeHandler={true}
          className="w-full h-full"
          config={{ displayModeBar: false }}
        />
      </div>
    </div>
  );
}
