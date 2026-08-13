import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';
import Plot from 'react-plotly.js';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ArrowLeft, Target } from 'lucide-react';

export default function WaterUsageDashboard() {
  const { id } = useParams();
  const [data, setData] = useState([]);
  const [adherence, setAdherence] = useState(0);
  const [chartImage, setChartImage] = useState(null);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!currentUser) return;
      try {
        const usageData = await api.getWaterUsage(id);
        const adData = await api.getAdherence(id);
        
        setData(usageData.data ? usageData.data : usageData);
        setAdherence(adData.adherence_percent || 0);
        if (adData.chart_image) {
            setChartImage(adData.chart_image);
        } else if (usageData.chart_image) {
            setChartImage(usageData.chart_image);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [id, currentUser]);

  if (loading) return <div>Loading...</div>;

  const dates = data.map(d => d.date);
  const amounts = data.map(d => d.total_mm || d.actual_amount_mm || 0);

  return (
    <div>
      <div className="mb-6 flex items-center">
        <Link to={`/field/${id}`} className="mr-4 p-2 bg-gray-100 rounded-full hover:bg-gray-200">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Water Usage Analytics</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border col-span-1 flex flex-col justify-center items-center">
          <Target className="w-12 h-12 text-purple-600 mb-2" />
          <h2 className="text-lg font-medium text-gray-600">Adherence Score</h2>
          <p className="text-4xl font-extrabold text-gray-900 mt-2">{adherence}%</p>
          <p className="text-sm text-gray-500 mt-2 text-center">Followed system recommendations</p>
          
          <div className="w-full mt-4 flex justify-center">
             <Plot
               data={[
                 {
                   values: [adherence, 100 - adherence],
                   labels: ['Adhered', 'Missed'],
                   type: 'pie',
                   hole: 0.4,
                   marker: { colors: ['#4ade80', '#f87171'] }
                 }
               ]}
               layout={{ width: 200, height: 200, showlegend: false, margin: { t: 10, b: 10, l: 10, r: 10 } }}
               config={{ displayModeBar: false }}
             />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border col-span-1 md:col-span-2">
          <h2 className="text-lg font-medium text-gray-800 mb-4">Water Usage Trend (mm) - Plotly</h2>
          <div className="h-64 flex justify-center">
            {data.length > 0 ? (
               <Plot
                 data={[
                   {
                     x: dates,
                     y: amounts,
                     type: 'scatter',
                     mode: 'lines+markers',
                     marker: { color: '#8884d8' },
                     name: 'Actual Amount'
                   }
                 ]}
                 layout={{ 
                    autosize: true, 
                    margin: { t: 10, r: 10, b: 30, l: 40 },
                    xaxis: { title: 'Date' },
                    yaxis: { title: 'Amount (mm)' }
                 }}
                 useResizeHandler={true}
                 style={{ width: '100%', height: '100%' }}
               />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                Not enough data yet
              </div>
            )}
          </div>
        </div>
      </div>
      
      {chartImage && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
            <h2 className="text-lg font-medium text-gray-800 mb-4">Matplotlib Generated Chart</h2>
            <div className="flex justify-center">
                <img src={`data:image/png;base64,${chartImage}`} alt="Water Usage Chart" className="max-w-full h-auto" />
            </div>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-medium text-gray-800 mb-4">Water Usage Trend (Recharts - Backup)</h2>
        <div className="h-64">
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <Line type="monotone" dataKey="actual_amount_mm" stroke="#8884d8" strokeWidth={3} dot={{ r: 4 }} />
                  <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                Not enough data yet
              </div>
            )}
        </div>
      </div>
    </div>
  );
}
