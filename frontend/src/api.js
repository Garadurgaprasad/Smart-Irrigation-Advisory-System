/**
 * api.js — Flask Backend API Client
 * ══════════════════════════════════
 * Smart Irrigation Advisory System
 * 
 * Centralized API client with JWT authentication.
 * All endpoints match the Flask backend routes exactly.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || '';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // Required for HttpOnly cookies
});

// Attach JWT token to every request


// ── Auth ──────────────────────────────────────────────────────────────

const login = async (email, password) => {
  const res = await apiClient.post('/api/auth/login', { email, password });
  return res.data;
};

const register = async (name, email, password, role) => {
  const res = await apiClient.post('/api/auth/register', { name, email, password, role });
  return res.data;
};


const logout = async () => {
  const res = await apiClient.post('/api/auth/logout');
  return res.data;
};

const verifyEmail = async (token) => {
  const res = await apiClient.post('/api/auth/verify-email', { token });
  return res.data;
};

const forgotPassword = async (email) => {
  const res = await apiClient.post('/api/auth/forgot-password', { email });
  return res.data;
};

const resetPassword = async (token, password) => {
  const res = await apiClient.post('/api/auth/reset-password', { token, password });
  return res.data;
};
\nconst getMe = async () => {
  const res = await apiClient.get('/api/auth/me');
  return res.data.user;
};

// ── Fields ────────────────────────────────────────────────────────────

const getFields = async () => {
  const res = await apiClient.get('/api/fields');
  return res.data;
};

const createField = async (fieldData) => {
  const res = await apiClient.post('/api/fields', fieldData);
  return res.data;
};

const getField = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}`);
  return res.data;
};

const updateField = async (fieldId, data) => {
  const res = await apiClient.put(`/api/fields/${fieldId}`, data);
  return res.data;
};

const deleteField = async (fieldId) => {
  const res = await apiClient.delete(`/api/fields/${fieldId}`);
  return res.data;
};

// ── Moisture ──────────────────────────────────────────────────────────

const logMoisture = async (fieldId, moisture_percent, source = 'manual') => {
  const res = await apiClient.post(`/api/fields/${fieldId}/moisture`, {
    moisture_percent,
    source,
  });
  return res.data;
};

const getMoistureHistory = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/moisture`);
  return res.data;
};

// ── Weather ───────────────────────────────────────────────────────────

const getWeather = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/weather`);
  return res.data;
};

// ── Advisory ──────────────────────────────────────────────────────────

const getRecommendation = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/recommendation`);
  return res.data;
};

// ── Irrigation Logging ────────────────────────────────────────────────

const logIrrigation = async (fieldId, data) => {
  const res = await apiClient.post(`/api/fields/${fieldId}/irrigate`, data);
  return res.data;
};

const getIrrigationLogs = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/irrigation-logs`);
  return res.data;
};

// ── Analytics ─────────────────────────────────────────────────────────

const getWaterUsage = async (fieldId, period = 'daily') => {
  const res = await apiClient.get(`/api/fields/${fieldId}/analytics/water-usage?period=${period}`);
  return res.data;
};

const getAdherence = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/analytics/adherence`);
  return res.data;
};

const getMoistureTrend = async (fieldId) => {
  const res = await apiClient.get(`/api/fields/${fieldId}/analytics/moisture`);
  return res.data;
};

// ── Admin Rules ───────────────────────────────────────────────────────

const getRules = async () => {
  const res = await apiClient.get('/api/admin/rules');
  return res.data;
};

const createRule = async (ruleData) => {
  const res = await apiClient.post('/api/admin/rules', ruleData);
  return res.data;
};

const updateRule = async (ruleId, ruleData) => {
  const res = await apiClient.put(`/api/admin/rules/${ruleId}`, ruleData);
  return res.data;
};

const deleteRule = async (ruleId) => {
  const res = await apiClient.delete(`/api/admin/rules/${ruleId}`);
  return res.data;
};

// ── System ────────────────────────────────────────────────────────────

const getHealth = async () => {
  const res = await apiClient.get('/api/health');
  return res.data;
};

const getCrops = async () => {
  const res = await apiClient.get('/api/crops');
  return res.data;
};

export default {
  login,
  register,
  getMe,\n  logout,\n  verifyEmail,\n  forgotPassword,\n  resetPassword,
  getFields,
  createField,
  getField,
  updateField,
  deleteField,
  logMoisture,
  getMoistureHistory,
  getWeather,
  getRecommendation,
  logIrrigation,
  getIrrigationLogs,
  getWaterUsage,
  getAdherence,
  getMoistureTrend,
  getRules,
  createRule,
  updateRule,
  deleteRule,
  getHealth,
  getCrops,
};
