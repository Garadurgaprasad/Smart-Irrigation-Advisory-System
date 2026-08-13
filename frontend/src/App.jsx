import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import FarmerDashboard from './pages/FarmerDashboard';
import FieldDetail from './pages/FieldDetail';
import WaterUsageDashboard from './pages/WaterUsageDashboard';
import AdminPanel from './pages/AdminPanel';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { currentUser, role } = useAuth();
  if (!currentUser) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(role)) return <Navigate to="/" replace />;
  return children;
};

function AppRoutes() {
  const { currentUser, role } = useAuth();
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {currentUser && <Navbar />}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/login" element={!currentUser ? <Login /> : <Navigate to="/" />} />
          <Route path="/register" element={!currentUser ? <Register /> : <Navigate to="/" />} />
          
          {/* Farmer Routes */}
          <Route path="/" element={
            <ProtectedRoute allowedRoles={['farmer', 'admin']}>
              {role === 'admin' ? <Navigate to="/admin" /> : <FarmerDashboard />}
            </ProtectedRoute>
          } />
          <Route path="/field/:id" element={
            <ProtectedRoute allowedRoles={['farmer']}>
              <FieldDetail />
            </ProtectedRoute>
          } />
          <Route path="/field/:id/analytics" element={
            <ProtectedRoute allowedRoles={['farmer']}>
              <WaterUsageDashboard />
            </ProtectedRoute>
          } />
          
          {/* Admin Routes */}
          <Route path="/admin" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminPanel />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
