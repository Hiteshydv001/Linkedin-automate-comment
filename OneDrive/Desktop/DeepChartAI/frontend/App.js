import React, { useState } from 'react';
import Plotly from 'plotly.js-dist-min';

function App() {
  const [query, setQuery] = useState('');
  const [file, setFile] = useState(null);
  const [jsonData, setJsonData] = useState('');
  const [manualData, setManualData] = useState('');
  const [chartType, setChartType] = useState('');
  const [chartData, setChartData] = useState(null);
  const [insights, setInsights] = useState('');
  const [error, setError] = useState(null);

  const chartOptions = ['line', 'bar', 'pie', 'scatter', 'heatmap'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setInsights('');

    const formData = new FormData();
    formData.append('query', query);
    if (chartType) formData.append('chart_type', chartType);
    if (file) formData.append('file', file);
    if (jsonData) formData.append('json_data', jsonData);
    if (manualData) formData.append('manual_data', manualData);

    try {
      const response = await fetch('http://localhost:8000/generate-chart/', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.status === "success") {
        setChartData(data);
        renderChart(data);
      } else {
        setError(data.detail);
      }
    } catch (err) {
      setError('Failed to generate chart');
    }
  };

  const handleAnalyzeTrends = async () => {
    if (!file) {
      setError('Upload a CSV file for trend analysis');
      return;
    }
    const formData = new FormData();
    formData.append('query', query);
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze-trends/', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.status === "success") {
        setInsights(data.insights);
      } else {
        setError(data.detail);
      }
    } catch (err) {
      setError('Failed to analyze trends');
    }
  };

  const renderChart = (data) => {
    const { chart_type, x_axis, y_axis, data: chartData } = data;
    const trace = {
      x: chartData[x_axis],
      y: chartData[y_axis],
      type: chart_type === 'pie' ? 'pie' : chart_type === 'heatmap' ? 'heatmap' : chart_type,
      ...(chart_type === 'pie' ? { labels: chartData[x_axis], values: chartData[y_axis] } : {}),
      ...(chart_type === 'heatmap' ? { z: chartData[y_axis] } : {})
    };
    const layout = {
      title: `${y_axis} vs ${x_axis}`,
      xaxis: { title: x_axis, tickangle: -45 },
      yaxis: { title: y_axis },
      autosize: true,
      margin: { l: 50, r: 50, b: 100, t: 100 },
    };
    Plotly.newPlot('chartContainer', [trace], layout, { responsive: true, displayModeBar: true });
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>AI Chart Builder</h1>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label>Query:</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Show me sales trends over time"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>

        <div>
          <label>Chart Type (optional):</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="">AI Suggested</option>
            {chartOptions.map(opt => (
              <option key={opt} value={opt}>{opt.charAt(0).toUpperCase() + opt.slice(1)}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Upload CSV:</label>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} style={{ marginTop: '5px' }} />
        </div>

        <div>
          <label>JSON Data:</label>
          <textarea
            value={jsonData}
            onChange={(e) => setJsonData(e.target.value)}
            placeholder='e.g., {"Date": ["2023-01-01", "2023-02-01"], "Sales": [100, 150]}'
            style={{ width: '100%', padding: '8px', marginTop: '5px', minHeight: '100px' }}
          />
        </div>

        <div>
          <label>Manual CSV Data:</label>
          <textarea
            value={manualData}
            onChange={(e) => setManualData(e.target.value)}
            placeholder="e.g., Date,Sales\n2023-01-01,100\n2023-02-01,150"
            style={{ width: '100%', padding: '8px', marginTop: '5px', minHeight: '100px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit" style={{ padding: '10px 20px', background: '#007BFF', color: 'white', border: 'none', cursor: 'pointer' }}>
            Generate Chart
          </button>
          <button
            type="button"
            onClick={handleAnalyzeTrends}
            style={{ padding: '10px 20px', background: '#28A745', color: 'white', border: 'none', cursor: 'pointer' }}
          >
            Analyze Trends
          </button>
        </div>
      </form>

      {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      
      {chartData && (
        <div style={{ marginTop: '20px' }}>
          <h3>Chart Type: {chartData.chart_type}</h3>
          <p>X-Axis: {chartData.x_axis}</p>
          <p>Y-Axis: {chartData.y_axis}</p>
          <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px' }}>{chartData.code}</pre>
          <div id="chartContainer" style={{ width: '100%', height: '500px', marginTop: '20px' }}></div>
        </div>
      )}

      {insights && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#f0f0f0', borderRadius: '5px' }}>
          <h3>Insights</h3>
          <p>{insights}</p>
        </div>
      )}
    </div>
  );
}

export default App;