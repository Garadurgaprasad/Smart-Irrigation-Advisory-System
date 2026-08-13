import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Droplet, Sparkles, User, ShieldCheck, ArrowRight } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('farmer@demo.com');
  const [password, setPassword] = useState('demo12345678');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const emailToUse = email.trim() || 'farmer@demo.com';
      const passToUse = password || 'demo12345678';
      await login(emailToUse, passToUse);
      navigate('/');
    } catch (err) {
      console.warn('Login fallback triggered:', err);
      // Ensure universal entry for hackathon demo
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail, demoRole) => {
    setEmail(demoEmail);
    setPassword('demo12345678');
    setLoading(true);
    login(demoEmail, 'demo12345678')
      .then(() => {
        if (demoRole === 'admin') navigate('/admin');
        else navigate('/');
      })
      .catch(() => {
        navigate('/');
      })
      .finally(() => setLoading(false));
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex flex-col items-center mb-6 text-center">
          <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 mb-3">
            <Droplet className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-2xl font-black text-gray-900 tracking-tight">Sign in to AgriSense</h2>
          <p className="text-sm text-gray-500 mt-1">Smart Irrigation Advisory & Water Optimization System</p>
          <div className="mt-2.5 inline-flex items-center space-x-1.5 px-3 py-1 bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold rounded-full">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Hackathon Demo Mode: Enter any credentials to login</span>
          </div>
        </div>

        {/* 1-Click Quick Demo Login Shortcuts */}
        <div className="space-y-2.5 mb-6">
          <button
            type="button"
            onClick={() => handleQuickLogin('farmer@demo.com', 'farmer')}
            disabled={loading}
            className="w-full flex items-center justify-between p-3 rounded-xl border border-emerald-200 bg-emerald-50/70 hover:bg-emerald-100 text-emerald-900 transition text-left group shadow-sm"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold">Quick Login as Farmer</div>
                <div className="text-[11px] text-emerald-700">Pre-loaded fields, sensor readings & advisory</div>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform" />
          </button>

          <button
            type="button"
            onClick={() => handleQuickLogin('admin@demo.com', 'admin')}
            disabled={loading}
            className="w-full flex items-center justify-between p-3 rounded-xl border border-indigo-200 bg-indigo-50/70 hover:bg-indigo-100 text-indigo-900 transition text-left group shadow-sm"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center flex-shrink-0">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold">Quick Login as Agronomist / Admin</div>
                <div className="text-[11px] text-indigo-700">Manage crop rules, thresholds & models</div>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-indigo-600 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>

        <div className="relative flex py-2 items-center mb-6">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="flex-shrink mx-4 text-xs uppercase font-bold text-gray-400">Or sign in with custom credentials</span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1">Email Address</label>
            <input
              type="text"
              placeholder="e.g. yourname@example.com"
              className="block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1">Password</label>
            <input
              type="password"
              placeholder="••••••••••••"
              className="block w-full rounded-xl border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border text-sm"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-lg shadow-blue-600/20 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none transition"
          >
            {loading ? 'Signing in...' : 'Sign in to Dashboard'}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-gray-500">
          New farm or agronomist?{' '}
          <Link to="/register" className="text-blue-600 hover:text-blue-700 font-bold">
            Create an Account
          </Link>
        </p>
      </div>
    </div>
  );
}
