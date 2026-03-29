import React, { useEffect, useRef, useState } from 'react';
import Plotly from 'plotly.js-dist-min';

export default function CRSPlotlyChart() {
  const chartRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/customers?limit=1000');
        const json = await res.json();
        const customers = json.customers;

        // Filter and map data for the plot
        // X: CRS Score, Y: Risk Score, Color: CRS Band
        const x = customers.map(c => c.crs_score || 0);
        const y = customers.map(c => c.risk_score || 0);
        const text = customers.map(c => `ID: ${c.customer_id}<br>CRS: ${c.crs_score?.toFixed(2)}<br>Risk: ${c.risk_score?.toFixed(2)}<br>Band: ${c.crs_band}`);
        
        const colors = customers.map(c => {
          if (c.crs_band === 'Reliable') return '#2dd4bf'; // teal-400
          if (c.crs_band === 'Moderate') return '#60a5fa'; // blue-400
          return '#f87171'; // rose-400
        });

        const data = [{
          x: x,
          y: y,
          mode: 'markers',
          type: 'scatter',
          text: text,
          hoverinfo: 'text',
          marker: {
            size: 8,
            color: colors,
            opacity: 0.6,
            line: { color: 'rgba(255,255,255,0.1)', width: 1 }
          }
        }];

        const layout = {
          autosize: true,
          height: 300,
          margin: { l: 40, r: 20, b: 40, t: 10 },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          showlegend: false,
          xaxis: { 
            title: { text: 'Reliability (CRS)', font: { size: 10, color: '#94a3b8' } },
            gridcolor: 'rgba(255,255,255,0.05)', 
            tickfont: { color: '#64748b', size: 9 },
            range: [0, 1]
          },
          yaxis: { 
            title: { text: 'Risk Score', font: { size: 10, color: '#94a3b8' } },
            gridcolor: 'rgba(255,255,255,0.05)', 
            tickfont: { color: '#64748b', size: 9 },
            range: [0, 1]
          },
          font: { family: 'Inter, sans-serif' }
        };

        const config = { responsive: true, displayModeBar: false };

        if (chartRef.current) {
          Plotly.newPlot(chartRef.current, data, layout, config);
        }
      } catch (err) {
        console.error("CRS Plotly fetch failed:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    const handleResize = () => {
      if (chartRef.current) Plotly.Plots.resize(chartRef.current);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) Plotly.purge(chartRef.current);
    };
  }, []);

  return (
    <div className="w-full h-full min-h-[300px] flex flex-col justify-center">
      {loading ? (
        <div className="flex justify-center items-center h-full">
          <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="flex-1 w-full" ref={chartRef}></div>
      )}
    </div>
  );
}
