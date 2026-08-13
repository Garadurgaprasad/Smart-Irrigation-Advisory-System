import React, { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import api from '../api';
import { ShieldCheck, Plus } from 'lucide-react';

export default function AdminPanel() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const { currentUser } = useAuth();
  
  const [newRule, setNewRule] = useState({
    crop_type: 'Wheat', growth_stage: 'Vegetative', water_requirement_mm_per_day: 5.0, moisture_threshold_percent: 40.0
  });

  const fetchRules = async () => {
    try {
      const data = await api.getRules();
      setRules(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) fetchRules();
  }, [currentUser]);

  const handleAddRule = async (e) => {
    e.preventDefault();
    try {
      await api.createRule(newRule);
      setNewRule({ crop_type: 'Wheat', growth_stage: 'Vegetative', water_requirement_mm_per_day: 5.0, moisture_threshold_percent: 40.0 });
      fetchRules();
    } catch (err) {
      console.error(err);
      alert("Failed to add rule");
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <div className="flex items-center mb-6">
        <ShieldCheck className="w-8 h-8 text-indigo-600 mr-3" />
        <h1 className="text-3xl font-bold text-gray-900">Admin Panel: Crop Rules</h1>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
        <h2 className="text-xl font-medium mb-4 flex items-center"><Plus className="w-5 h-5 mr-1"/> Add New Rule</h2>
        <form onSubmit={handleAddRule} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium">Crop Type</label>
            <input type="text" required className="mt-1 block w-full border rounded-md p-2" 
              value={newRule.crop_type} onChange={e => setNewRule({...newRule, crop_type: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium">Growth Stage</label>
            <input type="text" required className="mt-1 block w-full border rounded-md p-2" 
              value={newRule.growth_stage} onChange={e => setNewRule({...newRule, growth_stage: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium">Water Need (mm/day)</label>
            <input type="number" step="0.1" required className="mt-1 block w-full border rounded-md p-2" 
              value={newRule.water_requirement_mm_per_day} onChange={e => setNewRule({...newRule, water_requirement_mm_per_day: parseFloat(e.target.value)})} />
          </div>
          <div>
            <label className="block text-sm font-medium">Moisture Threshold (%)</label>
            <input type="number" step="0.1" required className="mt-1 block w-full border rounded-md p-2" 
              value={newRule.moisture_threshold_percent} onChange={e => setNewRule({...newRule, moisture_threshold_percent: parseFloat(e.target.value)})} />
          </div>
          <div className="lg:col-span-4 mt-2">
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">Save Rule</button>
          </div>
        </form>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Crop Type</th>
              <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Stage</th>
              <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Need (mm/d)</th>
              <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Threshold (%)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {rules.map(r => (
              <tr key={r.id}>
                <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 font-medium">{r.crop_type}</td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.growth_stage}</td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.water_requirement_mm_per_day}</td>
                <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{r.moisture_threshold_percent}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
