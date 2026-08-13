import React, { createContext, useContext, useEffect, useState } from 'react';
import api from './api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await api.getMe();
          setCurrentUser(userData);
          setRole(userData.role || 'farmer');
        } catch (e) {
          console.error("Error fetching me", e);
          localStorage.removeItem('token');
          setCurrentUser(null);
          setRole(null);
        }
      } else {
        setCurrentUser(null);
        setRole(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('token', data.token);
    setCurrentUser(data.user);
    setRole(data.user.role || 'farmer');
  };

  const register = async (name, email, password, roleInput) => {
    const data = await api.register(name, email, password, roleInput);
    localStorage.setItem('token', data.token);
    setCurrentUser(data.user);
    setRole(data.user.role || 'farmer');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    setRole(null);
  };

  const value = {
    currentUser,
    role,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
