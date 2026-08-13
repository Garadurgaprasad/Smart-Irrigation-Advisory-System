import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Droplet } from 'lucide-react';

export default function Navbar() {
  const { currentUser, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Droplet className="h-8 w-8 text-blue-600 mr-2" />
            <div className="flex flex-col">
              <span className="font-bold text-xl text-gray-900 leading-none mt-1">AgriSense</span>
              <span className="text-xs text-gray-500 mt-1">- by Quantum Coders</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {currentUser?.email || currentUser?.name} ({role})
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
