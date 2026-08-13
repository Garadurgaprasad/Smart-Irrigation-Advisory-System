import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import api from '../api';
import { PlusCircle, Sprout, Map } from 'lucide-react';

export default function FarmerDashboard() {
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const { currentUser } = useAuth();
  
  const [newField, setNewField] = useState({
    name: '', crop_type: 'Rice', area_acres: 1.0, current_growth_stage: 'Vegetative'
  });

  const fetchFields = async () => {
    try {
      const data = await api.getFields();
      setFields(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) fetchFields();
  }, [currentUser]);

  const handleAddField = async (e) => {
    e.preventDefault();
    try {
      await api.createField(newField);
      setShowAdd(false);
      setNewField({ name: '', crop_type: 'Rice', area_acres: 1.0, current_growth_stage: 'Vegetative' });
      fetchFields();
    } catch (err) {
      console.error(err);
      alert("Failed to add field");
    }
  };

  if (loading) return <div className="text-center py-12">Loading...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Fields</h1>
        <button 
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          <PlusCircle className="w-5 h-5 mr-2" />
          Add Field
        </button>
      </div>

      {showAdd && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
          <h2 className="text-lg font-medium mb-4">Add New Field</h2>
          <form onSubmit={handleAddField} className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="block text-sm font-medium">Field Name</label>
              <input type="text" required className="mt-1 block w-full border rounded-md p-2" 
                value={newField.name} onChange={e => setNewField({...newField, name: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium">Crop Type</label>
              <select className="mt-1 block w-full border rounded-md p-2"
                value={newField.crop_type} onChange={e => setNewField({...newField, crop_type: e.target.value})}>
                <option>Rice</option>
                <option>Maize</option>
                <option>Chili</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium">Area (Acres)</label>
              <input type="number" step="0.1" required className="mt-1 block w-full border rounded-md p-2"
                value={newField.area_acres} onChange={e => setNewField({...newField, area_acres: parseFloat(e.target.value)})} />
            </div>
            <div>
              <label className="block text-sm font-medium">Current Growth Stage</label>
              <select className="mt-1 block w-full border rounded-md p-2"
                value={newField.current_growth_stage} onChange={e => setNewField({...newField, current_growth_stage: e.target.value})}>
                <option>Germination</option>
                <option>Vegetative</option>
                <option>Flowering</option>
                <option>Maturity</option>
              </select>
            </div>
            <div className="sm:col-span-2 lg:col-span-4">
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Save Field</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {fields.length === 0 && <p className="text-gray-500">No fields added yet. Add one to get started.</p>}
        {fields.map(field => (
          <Link key={field.id} to={`/field/${field.id}`} className="block">
            <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-4">
                <Map className="w-8 h-8 text-blue-500 mr-3" />
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{field.name}</h3>
                  <p className="text-sm text-gray-500">{field.area_acres} Acres</p>
                </div>
              </div>
              <div className="flex items-center text-sm text-gray-700 mt-2">
                <Sprout className="w-5 h-5 text-green-500 mr-2" />
                <span className="font-medium mr-1">{field.crop_type}:</span> {field.current_growth_stage}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
