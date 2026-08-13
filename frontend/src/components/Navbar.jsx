import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Droplet, Sparkles, Map, Sliders, ShieldCheck, LogOut, Activity } from 'lucide-react';

export default function Navbar() {
  const { currentUser, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2.5">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-md shadow-blue-500/20">
                <Droplet className="h-6 w-6 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-xl text-gray-900 leading-none">AgriSense</span>
                <span className="text-[10px] text-gray-400 font-medium tracking-wider uppercase mt-1">Smart Advisory</span>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`
                }
              >
                <Map className="w-4 h-4" />
                <span>My Fields</span>
              </NavLink>

              <NavLink
                to="/advisory"
                className={({ isActive }) =>
                  `flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`
                }
              >
                <Sparkles className="w-4 h-4 text-blue-600" />
                <span>Advisory Engine</span>
                <span className="px-1.5 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-black rounded-md ml-1">
                  NEW
                </span>
              </NavLink>

              {role === 'admin' && (
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    `flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold transition ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`
                  }
                >
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <span>Admin Rules</span>
                </NavLink>
              )}
            </div>
          </div>

          {/* User Profile & Logout */}
          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-xs font-bold text-gray-900 leading-tight">
                {currentUser?.name || currentUser?.email?.split('@')[0]}
              </span>
              <span className="text-[11px] text-gray-500 font-medium capitalize">
                {role === 'admin' ? 'Agronomist (Admin)' : 'Farmer Account'}
              </span>
            </div>

            <button
              onClick={handleLogout}
              className="px-3.5 py-2 border border-gray-200 rounded-xl text-xs font-bold text-gray-700 bg-gray-50 hover:bg-red-50 hover:text-red-700 hover:border-red-200 transition flex items-center space-x-1.5"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
