import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';
import { Droplet, CloudRain, Activity, CheckCircle, Clock } from 'lucide-react';

export default function FieldDetail() {
  const { id } = useParams();
  const [field, setField] = useState(null);
  const [activeTab, setActiveTab] = useState('log');
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();
  
  // Forms
  const [moisture, setMoisture] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [history, setHistory] = useState({ readings: [], logs: [] });

  const fetchField = async () => {
    try {
      const data = await api.getField(id);
      setField(data);
    } catch (err) {
      console.error(err);
      setField(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchWeather = async () => {
    try {
      const data = await api.getWeather(id);
      setWeatherData(data);
    } catch (err) {
      console.error("Failed to fetch weather", err);
    }
  };

  const loadRecommendation = async () => {
    try {
      const data = await api.getRecommendation(id);
      setRecommendation(data);
    } catch (err) {
      console.error(err);
      setRecommendation(null);
    }
  };

  const fetchHistory = async () => {
    try {
      const readings = await api.getMoistureHistory(id);
      const logs = await api.getIrrigationLogs(id);
      setHistory({ readings, logs });
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchField();
      fetchWeather();
    }
  }, [id, currentUser]);

  const handleLogMoisture = async (e) => {
    e.preventDefault();
    try {
      await api.logMoisture(id, parseFloat(moisture), 'manual');
      alert("Reading logged successfully!");
      setMoisture('');
      setActiveTab('recommendation');
      loadRecommendation();
    } catch (err) {
      console.error(err);
      alert("Failed to log moisture");
    }
  };

  const handleLogIrrigation = async (actionTaken) => {
    try {
      const amount = actionTaken === 'irrigated' ? recommendation.amount_mm : 0;
      await api.logIrrigation(id, {
        recommendation: recommendation.recommendation,
        action_taken: actionTaken,
        recommended_amount_mm: recommendation.amount_mm || 0,
        actual_amount_mm: amount,
        reason: recommendation.reason || '',
      });
      alert("Action logged successfully!");
      setRecommendation(null);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!field) return <div>Field not found</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{field.name}</h1>
          <p className="text-gray-600">{field.crop_type || field.crop} • {field.current_growth_stage || field.growth_stage}</p>
        </div>
        <Link to={`/field/${id}/analytics`} className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Analytics
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="flex border-b">
          <button onClick={() => setActiveTab('log')} className={`flex-1 py-4 text-center font-medium ${activeTab === 'log' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}>Log Reading</button>
          <button onClick={() => { setActiveTab('recommendation'); loadRecommendation(); }} className={`flex-1 py-4 text-center font-medium ${activeTab === 'recommendation' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}>Recommendation</button>
          <button onClick={() => { setActiveTab('history'); fetchHistory(); }} className={`flex-1 py-4 text-center font-medium ${activeTab === 'history' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}>History</button>
        </div>

        <div className="p-6">
          {activeTab === 'log' && (
            <div className="max-w-xl mx-auto space-y-8">
              <div className="bg-blue-50 p-4 rounded-lg flex items-start">
                <CloudRain className="w-6 h-6 text-blue-500 mr-3 mt-1" />
                <div>
                  <h3 className="font-semibold text-blue-900">Current Weather Forecast</h3>
                  {weatherData ? (
                    <p className="text-blue-800 text-sm mt-1">
                      Rain Probability: {weatherData.rain_probability_percent}% <br/>
                      Expected Rainfall: {weatherData.expected_rainfall_mm} mm
                    </p>
                  ) : (
                    <p className="text-sm text-blue-600 mt-1">Fetching weather...</p>
                  )}
                </div>
              </div>

              <form onSubmit={handleLogMoisture} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Soil Moisture (%)</label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Droplet className="h-5 w-5 text-gray-400" />
                    </div>
                    <input 
                      type="number" min="0" max="100" step="0.1" required
                      className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md p-3 border"
                      placeholder="e.g. 45"
                      value={moisture} onChange={e => setMoisture(e.target.value)}
                    />
                  </div>
                </div>
                <button type="submit" className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                  Save Reading & Get Recommendation
                </button>
              </form>
            </div>
          )}

          {activeTab === 'recommendation' && (
            <div className="max-w-2xl mx-auto">
              {!recommendation ? (
                <div className="text-center py-12 text-gray-500">
                  <p>Loading recommendation or no recent data available...</p>
                </div>
              ) : (
                <div className={`p-8 rounded-2xl border-2 ${recommendation.recommendation === 'irrigate' ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
                  <div className="text-center">
                    <h2 className={`text-4xl font-extrabold mb-2 ${recommendation.recommendation === 'irrigate' ? 'text-blue-700' : 'text-green-700'}`}>
                      {recommendation.recommendation === 'irrigate' ? `Irrigate Now: ${recommendation.amount_mm} mm` : 'Wait'}
                    </h2>
                    <p className="text-lg text-gray-700 mt-4 bg-white p-4 rounded-xl shadow-sm inline-block">
                      {recommendation.reason}
                    </p>
                  </div>
                  
                  <div className="mt-8 flex justify-center space-x-4">
                    <button onClick={() => handleLogIrrigation('irrigated')} className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                      <CheckCircle className="w-5 h-5 mr-2" /> Mark as Irrigated
                    </button>
                    <button onClick={() => handleLogIrrigation('skipped')} className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium">
                      <Clock className="w-5 h-5 mr-2" /> Mark as Skipped
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div>
              <h3 className="text-lg font-bold mb-4">Moisture Readings</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg mb-8">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Date</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Moisture (%)</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {history.readings.map(r => (
                      <tr key={r.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">{r.timestamp ? new Date(r.timestamp).toLocaleString() : (r.created_at ? new Date(r.created_at).toLocaleString() : 'Just now')}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.moisture_percent}%</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.source || 'manual'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <h3 className="text-lg font-bold mb-4">Irrigation Actions</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Date</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Recommended</th>
                      <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Action Taken</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {history.logs.map(r => (
                      <tr key={r.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">{r.logged_at ? new Date(r.logged_at).toLocaleString() : 'Just now'}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.recommendation} ({r.recommended_amount_mm}mm)</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm font-medium">
                          <span className={r.action_taken === 'irrigated' ? 'text-blue-600' : 'text-gray-500'}>{r.action_taken}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
