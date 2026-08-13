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
      try {
        const userData = await api.getMe();
        setCurrentUser(userData);
        setRole(userData.role || 'farmer');
      } catch (e) {
        // Not logged in or cookie expired
        setCurrentUser(null);
        setRole(null);
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    setCurrentUser(data.user);
    setRole(data.user.role || 'farmer');
  };

  const register = async (name, email, password, roleInput) => {
    await api.register(name, email, password, roleInput);
    // Do NOT log them in automatically, they must verify their email first!
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.error(e);
    }
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
