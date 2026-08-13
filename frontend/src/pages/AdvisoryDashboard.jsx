import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../AuthContext';
import {
  Droplet,
  CloudRain,
  Sun,
  Wind,
  Gauge,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Zap,
  TrendingDown,
  Info,
  Sliders,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  ArrowRight,
  ShieldAlert,
  Sprout,
  Activity,
  Maximize2
} from 'lucide-react';

export default function AdvisoryDashboard() {
  const { currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('matrix'); // 'matrix' | 'simulator' | 'schedule' | 'agronomy'
  const [loading, setLoading] = useState(true);

  // Farm Matrix State
  const [farmData, setFarmData] = useState({ fields_advisory: [], summary: {} });
  const [filterCrop, setFilterCrop] = useState('all');
  const [filterUrgency, setFilterUrgency] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFieldForAction, setSelectedFieldForAction] = useState(null);
  const [actionSuccess, setActionSuccess] = useState('');

  // Simulator / What-If State
  const [cropsList, setCropsList] = useState([]);
  const [soilsList, setSoilsList] = useState({});
  const [methodsList, setMethodsList] = useState({});
  const [simParams, setSimParams] = useState({
    crop_type: 'Rice',
    growth_stage: 'Vegetative',
    soil_type: 'Clay Loam',
    irrigation_method: 'Drip',
    moisture_percent: 38.0,
    rain_probability_percent: 15.0,
    expected_rainfall_mm: 0.0,
    field_area_acres: 2.0,
    temperature_c: 33.0,
    humidity_percent: 55.0,
    wind_speed_kmh: 12.0,
    pump_hp: 5.0,
  });
  const [simResult, setSimResult] = useState(null);
  const [simSchedule, setSimSchedule] = useState([]);
  const [simLoading, setSimLoading] = useState(false);
  const [bulletinLang, setBulletinLang] = useState('en'); // 'en' | 'hi' | 'te'
  const [copiedBulletin, setCopiedBulletin] = useState(false);

  // Initial Data Fetch
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [allFieldsRes, cropsRes, soilsRes, methodsRes] = await Promise.all([
        api.getAllFieldsAdvisory().catch(() => ({ fields_advisory: [], summary: {} })),
        api.getAdvisoryCrops().catch(() => []),
        api.getAdvisorySoils().catch(() => ({})),
        api.getAdvisoryMethods().catch(() => ({})),
      ]);
      setFarmData(allFieldsRes || { fields_advisory: [], summary: {} });
      setCropsList(cropsRes || []);
      setSoilsList(soilsRes || {});
      setMethodsList(methodsRes || {});
    } catch (err) {
      console.error('Failed to load advisory dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  // Run Simulator
  const runSimulation = async (paramsToRun) => {
    try {
      setSimLoading(true);
      const res = await api.calculateAdvisory(paramsToRun || simParams);
      setSimResult(res.advisory);
      setSimSchedule(res.schedule || []);
    } catch (err) {
      console.error('Simulation calculation failed:', err);
    } finally {
      setSimLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    runSimulation(simParams);
  }, []);

  // Quick recalculate when sim params change
  const handleSimParamChange = (key, value) => {
    const updated = { ...simParams, [key]: value };
    setSimParams(updated);
    runSimulation(updated);
  };

  // Handle Action Logging (Quick Irrigate from Matrix)
  const handleQuickIrrigate = async (field) => {
    try {
      const amount = field.gross_amount_mm || field.amount_mm || 0;
      await api.logIrrigation(field.field_id, {
        recommendation: field.recommendation || 'irrigate',
        action_taken: 'irrigated',
        recommended_amount_mm: amount,
        actual_amount_mm: amount,
        reason: field.reason || 'Irrigated via Advisory Matrix',
      });
      setActionSuccess(`Logged ${amount} mm irrigation for ${field.field_name}!`);
      setTimeout(() => setActionSuccess(''), 4000);
      fetchDashboardData();
    } catch (err) {
      console.error('Failed to log irrigation:', err);
    }
  };

  // Copy bulletin to clipboard
  const handleCopyBulletin = () => {
    if (!simResult?.bulletins?.[bulletinLang]) return;
    navigator.clipboard.writeText(simResult.bulletins[bulletinLang]);
    setCopiedBulletin(true);
    setTimeout(() => setCopiedBulletin(false), 2500);
  };

  // Filtered fields in matrix
  const filteredFields = useMemo(() => {
    return (farmData.fields_advisory || []).filter((f) => {
      const matchesCrop = filterCrop === 'all' || f.crop_type?.toLowerCase() === filterCrop.toLowerCase();
      const matchesUrgency =
        filterUrgency === 'all' ||
        (filterUrgency === 'critical' && f.status === 'IRRIGATE_IMMEDIATELY') ||
        (filterUrgency === 'action' && f.recommendation === 'irrigate') ||
        (filterUrgency === 'optimal' && f.status === 'ADEQUATE_MOISTURE') ||
        (filterUrgency === 'rain' && f.status === 'RAIN_EXPECTED_WAIT');
      const matchesSearch =
        !searchQuery ||
        f.field_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        f.crop_type?.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCrop && matchesUrgency && matchesSearch;
    });
  }, [farmData, filterCrop, filterUrgency, searchQuery]);

  // Unique crops for filter
  const uniqueCrops = useMemo(() => {
    const set = new Set((farmData.fields_advisory || []).map((f) => f.crop_type).filter(Boolean));
    return Array.from(set);
  }, [farmData]);

  // Distinct crop types from reference
  const availableCropNames = useMemo(() => {
    const set = new Set(cropsList.map((c) => c.crop_type));
    return Array.from(set);
  }, [cropsList]);

  // Growth stages available for currently selected crop in simulator
  const availableStagesForCrop = useMemo(() => {
    return cropsList
      .filter((c) => c.crop_type.toLowerCase() === simParams.crop_type.toLowerCase())
      .map((c) => c.growth_stage);
  }, [cropsList, simParams.crop_type]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-gray-600 font-medium">Loading Smart Advisory Engine & Farm Intelligence...</p>
      </div>
    );
  }

  const summary = farmData.summary || {};

  return (
    <div className="space-y-8 pb-12">
      {/* ── Top Header & KPI Ribbon ── */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-semibold uppercase tracking-wider mb-3 border border-blue-500/30">
              <Sparkles className="w-3.5 h-3.5" />
              <span>FAO-56 Agronomic Intelligence Engine</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">Smart Advisory Dashboard</h1>
            <p className="text-slate-300 mt-2 max-w-2xl text-sm sm:text-base leading-relaxed">
              Multi-factor root zone water balance, evapotranspiration (<span className="font-mono text-blue-300">ETc = Kc × ET0</span>), 
              soil moisture thresholds, effective rain credits, and pump runtime optimizer.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setActiveTab('simulator')}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-lg transition flex items-center space-x-2 text-sm"
            >
              <Sliders className="w-4 h-4" />
              <span>What-If Simulator</span>
            </button>
            <button
              onClick={fetchDashboardData}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl border border-slate-700 transition flex items-center space-x-2 text-sm"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Refresh Farm Data</span>
            </button>
          </div>
        </div>

        {/* KPI Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mt-8 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50">
            <span className="text-xs text-slate-400 font-medium">Fields Monitored</span>
            <div className="text-2xl font-bold text-white mt-1">{summary.total_fields || 0}</div>
            <span className="text-xs text-slate-500 mt-1 block">Active plots</span>
          </div>
          <div className="bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50">
            <span className="text-xs text-amber-400 font-medium">Immediate Water Needed</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">{summary.action_needed_count || 0}</div>
            <span className="text-xs text-slate-400 mt-1 block">{summary.critical_count || 0} critically dry</span>
          </div>
          <div className="bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50">
            <span className="text-xs text-blue-400 font-medium">Total Volume Needed</span>
            <div className="text-2xl font-bold text-blue-300 mt-1">{summary.total_water_m3 || 0} m³</div>
            <span className="text-xs text-slate-400 mt-1 block">{(summary.total_water_litres || 0).toLocaleString()} L</span>
          </div>
          <div className="bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50">
            <span className="text-xs text-emerald-400 font-medium">Rain Savings</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{summary.water_saved_m3 || 0} m³</div>
            <span className="text-xs text-slate-400 mt-1 block">{summary.rain_wait_count || 0} fields waiting rain</span>
          </div>
          <div className="bg-slate-800/50 backdrop-blur p-4 rounded-xl border border-slate-700/50 col-span-2 sm:col-span-1">
            <span className="text-xs text-purple-400 font-medium">Optimal Soil Health</span>
            <div className="text-2xl font-bold text-purple-300 mt-1">{summary.optimal_count || 0}</div>
            <span className="text-xs text-slate-400 mt-1 block">Adequate moisture buffer</span>
          </div>
        </div>
      </div>

      {/* Success Banner */}
      {actionSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl flex items-center justify-between shadow-sm animate-fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="text-sm font-medium">{actionSuccess}</span>
          </div>
          <button onClick={() => setActionSuccess('')} className="text-emerald-600 hover:text-emerald-800 text-sm font-bold">×</button>
        </div>
      )}

      {/* ── Navigation Tabs ── */}
      <div className="flex border-b border-gray-200 bg-white rounded-t-xl px-4 pt-2 shadow-sm overflow-x-auto">
        <button
          onClick={() => setActiveTab('matrix')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'matrix'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50 rounded-t-lg'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Farm Status Matrix</span>
          <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-bold">
            {farmData.fields_advisory?.length || 0}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('simulator')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'simulator'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50 rounded-t-lg'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Sliders className="w-4 h-4" />
          <span>"What-If" Advisory Simulator</span>
          <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded-full text-xs font-bold">Live</span>
        </button>

        <button
          onClick={() => setActiveTab('schedule')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'schedule'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50 rounded-t-lg'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>7-Day Predictive Planner</span>
        </button>

        <button
          onClick={() => setActiveTab('agronomy')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'agronomy'
              ? 'border-blue-600 text-blue-600 bg-blue-50/50 rounded-t-lg'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Crop Agronomic Guide & Kc</span>
        </button>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* TAB 1: FARM STATUS MATRIX                                          */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {activeTab === 'matrix' && (
        <div className="space-y-6">
          {/* Filters and Search Bar */}
          <div className="bg-white p-4 rounded-xl shadow-sm border flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Filter by:</span>
              <select
                value={filterUrgency}
                onChange={(e) => setFilterUrgency(e.target.value)}
                className="text-sm border rounded-lg px-3 py-2 bg-gray-50 text-gray-700 font-medium focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses ({farmData.fields_advisory?.length || 0})</option>
                <option value="critical">Critical Moisture Only</option>
                <option value="action">Action Needed (Irrigate)</option>
                <option value="rain">Waiting for Rain</option>
                <option value="optimal">Adequate / Optimal</option>
              </select>

              {uniqueCrops.length > 0 && (
                <select
                  value={filterCrop}
                  onChange={(e) => setFilterCrop(e.target.value)}
                  className="text-sm border rounded-lg px-3 py-2 bg-gray-50 text-gray-700 font-medium focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Crops ({uniqueCrops.length})</option>
                  {uniqueCrops.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="w-full md:w-72">
              <input
                type="text"
                placeholder="Search field name or crop..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-sm border rounded-lg px-3 py-2 bg-gray-50 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Field Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredFields.length === 0 ? (
              <div className="col-span-full py-16 text-center bg-white rounded-2xl border border-dashed border-gray-300">
                <Sprout className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <h3 className="text-lg font-bold text-gray-800">No fields match selected filters</h3>
                <p className="text-sm text-gray-500 mt-1">Try resetting the filter or search query</p>
                <button
                  onClick={() => {
                    setFilterCrop('all');
                    setFilterUrgency('all');
                    setSearchQuery('');
                  }}
                  className="mt-4 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-semibold hover:bg-blue-100"
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              filteredFields.map((field) => {
                const isCritical = field.status === 'IRRIGATE_IMMEDIATELY';
                const isIrrigate = field.recommendation === 'irrigate';
                const isRainWait = field.status === 'RAIN_EXPECTED_WAIT';
                const isOptimal = field.status === 'ADEQUATE_MOISTURE';

                let badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-200';
                let badgeLabel = 'OPTIMAL BUFFER';
                if (isCritical) {
                  badgeColor = 'bg-red-100 text-red-800 border-red-200 animate-pulse';
                  badgeLabel = 'CRITICAL DEFICIT';
                } else if (isIrrigate) {
                  badgeColor = 'bg-amber-100 text-amber-800 border-amber-200';
                  badgeLabel = 'IRRIGATE TODAY';
                } else if (isRainWait) {
                  badgeColor = 'bg-blue-100 text-blue-800 border-blue-200';
                  badgeLabel = 'RAIN EXPECTED';
                }

                const currentMoisture = field.moisture_percent || 0;
                const threshold = field.threshold_percent || 50;

                return (
                  <div
                    key={field.field_id}
                    className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-gray-200 p-6 flex flex-col justify-between"
                  >
                    <div>
                      {/* Top Field Badge Header */}
                      <div className="flex items-start justify-between gap-2 mb-3">
                        <div>
                          <h3 className="font-bold text-xl text-gray-900 leading-snug">{field.field_name}</h3>
                          <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                            <span className="font-semibold text-gray-700">{field.crop_type}</span>
                            <span>•</span>
                            <span>{field.growth_stage}</span>
                            <span>•</span>
                            <span>{field.area_acres} Acres</span>
                          </div>
                        </div>
                        <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${badgeColor} whitespace-nowrap`}>
                          {badgeLabel}
                        </span>
                      </div>

                      {/* Soil Moisture Progress Gauge */}
                      <div className="mt-4 bg-gray-50 p-3.5 rounded-xl border border-gray-100">
                        <div className="flex justify-between items-center text-xs font-semibold text-gray-700 mb-1.5">
                          <span className="flex items-center">
                            <Droplet className="w-3.5 h-3.5 text-blue-500 mr-1" />
                            Soil Moisture
                          </span>
                          <span className={`text-sm font-extrabold ${currentMoisture < threshold ? 'text-amber-600' : 'text-emerald-600'}`}>
                            {currentMoisture.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 relative overflow-hidden">
                          <div
                            className={`h-3 rounded-full transition-all ${
                              currentMoisture < threshold ? 'bg-amber-500' : 'bg-emerald-500'
                            }`}
                            style={{ width: `${Math.min(100, (currentMoisture / 80) * 100)}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-[11px] text-gray-400 mt-1">
                          <span>0% (Dry)</span>
                          <span className="text-gray-600 font-medium">Threshold: {threshold}%</span>
                          <span>80% (Sat)</span>
                        </div>
                      </div>

                      {/* Agronomic Recommendations Box */}
                      <div className="mt-4 p-3.5 bg-blue-50/60 rounded-xl border border-blue-100 text-xs text-gray-700 space-y-2">
                        <p className="font-medium text-blue-950 leading-relaxed">{field.reason}</p>
                        
                        {isIrrigate && (
                          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-blue-200/60">
                            <div>
                              <span className="text-gray-500 block text-[11px]">Water Volume</span>
                              <span className="font-bold text-blue-800 text-sm">
                                {field.gross_amount_mm || field.amount_mm} mm ({Math.round(field.total_litres || 0).toLocaleString()} L)
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500 block text-[11px]">Pump Runtime (5HP)</span>
                              <span className="font-bold text-slate-800 text-sm">
                                {field.pump_runtime?.formatted || 'N/A'}
                              </span>
                            </div>
                          </div>
                        )}

                        {field.recommended_window && (
                          <div className="flex items-center text-[11px] text-slate-600 pt-1">
                            <Clock className="w-3.5 h-3.5 mr-1 text-slate-400 flex-shrink-0" />
                            <span>Window: {field.recommended_window}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Footer */}
                    <div className="mt-5 pt-4 border-t border-gray-100 flex items-center gap-2">
                      <Link
                        to={`/field/${field.field_id}`}
                        className="flex-1 text-center py-2 px-3 bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-semibold rounded-lg transition"
                      >
                        Field View
                      </Link>

                      {isIrrigate && (
                        <button
                          onClick={() => handleQuickIrrigate(field)}
                          className="flex-1 py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition flex items-center justify-center space-x-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                          <span>Mark Irrigated</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* TAB 2: INTERACTIVE "WHAT-IF" SIMULATOR & PLAYGROUND                 */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {activeTab === 'simulator' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Panel (Left 5 Cols) */}
          <div className="lg:col-span-5 bg-white p-6 rounded-2xl shadow-sm border space-y-6">
            <div className="border-b pb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <Sliders className="w-5 h-5 text-blue-600 mr-2" />
                Scenario Parameter Controls
              </h2>
              <p className="text-xs text-gray-500 mt-1">
                Tweak field, soil, crop, and weather parameters to see the instant live decision.
              </p>
            </div>

            {/* Crop & Stage */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Crop Type</label>
                <select
                  value={simParams.crop_type}
                  onChange={(e) => handleSimParamChange('crop_type', e.target.value)}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                >
                  {availableCropNames.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Growth Stage</label>
                <select
                  value={simParams.growth_stage}
                  onChange={(e) => handleSimParamChange('growth_stage', e.target.value)}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                >
                  {availableStagesForCrop.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Soil & Irrigation Method */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Soil Texture</label>
                <select
                  value={simParams.soil_type}
                  onChange={(e) => handleSimParamChange('soil_type', e.target.value)}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                >
                  {Object.keys(soilsList).map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Irrigation Method</label>
                <select
                  value={simParams.irrigation_method}
                  onChange={(e) => handleSimParamChange('irrigation_method', e.target.value)}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                >
                  {Object.keys(methodsList).map((m) => (
                    <option key={m} value={m}>
                      {m} ({Math.round((methodsList[m]?.efficiency || 0.8) * 100)}% Eff)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Moisture Slider */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold text-gray-700">Current Soil Moisture</label>
                <span className="text-sm font-extrabold text-blue-600">{simParams.moisture_percent}%</span>
              </div>
              <input
                type="range"
                min="5"
                max="85"
                step="1"
                value={simParams.moisture_percent}
                onChange={(e) => handleSimParamChange('moisture_percent', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>5% (Wilting)</span>
                <span>40%</span>
                <span>85% (Saturated)</span>
              </div>
            </div>

            {/* Weather Sliders */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-gray-700">Rain Probability</label>
                  <span className="text-xs font-bold text-indigo-600">{simParams.rain_probability_percent}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={simParams.rain_probability_percent}
                  onChange={(e) => handleSimParamChange('rain_probability_percent', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-gray-700">Forecast Rain (mm)</label>
                  <span className="text-xs font-bold text-indigo-600">{simParams.expected_rainfall_mm} mm</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="35"
                  step="1"
                  value={simParams.expected_rainfall_mm}
                  onChange={(e) => handleSimParamChange('expected_rainfall_mm', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
              </div>
            </div>

            {/* Area & Pump Power */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Field Area (Acres)</label>
                <input
                  type="number"
                  min="0.1"
                  max="50"
                  step="0.1"
                  value={simParams.field_area_acres}
                  onChange={(e) => handleSimParamChange('field_area_acres', parseFloat(e.target.value) || 1)}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Pump Motor Power</label>
                <select
                  value={simParams.pump_hp}
                  onChange={(e) => handleSimParamChange('pump_hp', parseFloat(e.target.value))}
                  className="w-full text-sm border rounded-lg p-2.5 bg-gray-50 font-medium"
                >
                  <option value={2.0}>2.0 HP (Small Monoblock)</option>
                  <option value={3.0}>3.0 HP</option>
                  <option value={5.0}>5.0 HP (Standard Agri)</option>
                  <option value={7.5}>7.5 HP</option>
                  <option value={10.0}>10.0 HP (High Discharge)</option>
                </select>
              </div>
            </div>

            {/* Ambient Conditions */}
            <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs">
              <div>
                <span className="text-gray-500 block">Temp (°C)</span>
                <input
                  type="number"
                  value={simParams.temperature_c}
                  onChange={(e) => handleSimParamChange('temperature_c', parseFloat(e.target.value) || 30)}
                  className="w-full bg-white border rounded px-2 py-1 mt-1 font-bold"
                />
              </div>
              <div>
                <span className="text-gray-500 block">Humidity (%)</span>
                <input
                  type="number"
                  value={simParams.humidity_percent}
                  onChange={(e) => handleSimParamChange('humidity_percent', parseFloat(e.target.value) || 60)}
                  className="w-full bg-white border rounded px-2 py-1 mt-1 font-bold"
                />
              </div>
              <div>
                <span className="text-gray-500 block">Wind (km/h)</span>
                <input
                  type="number"
                  value={simParams.wind_speed_kmh}
                  onChange={(e) => handleSimParamChange('wind_speed_kmh', parseFloat(e.target.value) || 10)}
                  className="w-full bg-white border rounded px-2 py-1 mt-1 font-bold"
                />
              </div>
            </div>
          </div>

          {/* Live Decision & Analytical Report (Right 7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            {simResult ? (
              <>
                {/* Decision Verdict Banner */}
                <div
                  className={`p-6 rounded-2xl border-2 transition-all shadow-md ${
                    simResult.recommendation === 'irrigate'
                      ? 'bg-gradient-to-br from-blue-50 via-white to-blue-50/30 border-blue-300'
                      : 'bg-gradient-to-br from-emerald-50 via-white to-emerald-50/30 border-emerald-300'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <span className="text-xs font-extrabold uppercase tracking-wider text-gray-500">Advisory Engine Output</span>
                      <h3
                        className={`text-3xl font-black mt-1 ${
                          simResult.recommendation === 'irrigate' ? 'text-blue-700' : 'text-emerald-700'
                        }`}
                      >
                        {simResult.recommendation === 'irrigate'
                          ? `⚡ IRRIGATE: ${simResult.gross_amount_mm} mm`
                          : '✓ HOLD / ADEQUATE'}
                      </h3>
                    </div>

                    <div className="flex flex-col sm:items-end">
                      <span
                        className={`px-3 py-1 text-xs font-bold rounded-full border ${
                          simResult.status === 'IRRIGATE_IMMEDIATELY'
                            ? 'bg-red-100 text-red-800 border-red-200 animate-pulse'
                            : simResult.recommendation === 'irrigate'
                            ? 'bg-blue-100 text-blue-800 border-blue-200'
                            : 'bg-emerald-100 text-emerald-800 border-emerald-200'
                        }`}
                      >
                        {simResult.status.replace(/_/g, ' ')}
                      </span>
                      <span className="text-xs text-gray-500 mt-1.5 font-medium">
                        Confidence: <strong className="text-gray-900">{simResult.confidence_score}%</strong>
                      </span>
                    </div>
                  </div>

                  <p className="mt-4 text-sm text-gray-800 bg-white/80 backdrop-blur p-4 rounded-xl border leading-relaxed">
                    {simResult.reason}
                  </p>

                  {/* Key Numerical Metrics Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                    <div className="bg-white p-3 rounded-xl border text-center">
                      <span className="text-[11px] text-gray-500 uppercase font-semibold">Gross Water</span>
                      <div className="text-lg font-black text-blue-700 mt-0.5">{simResult.gross_amount_mm} mm</div>
                      <span className="text-[10px] text-gray-400">{simResult.net_amount_mm} mm net</span>
                    </div>
                    <div className="bg-white p-3 rounded-xl border text-center">
                      <span className="text-[11px] text-gray-500 uppercase font-semibold">Total Volume</span>
                      <div className="text-lg font-black text-slate-800 mt-0.5">{simResult.total_m3} m³</div>
                      <span className="text-[10px] text-gray-400">{Math.round(simResult.total_litres).toLocaleString()} L</span>
                    </div>
                    <div className="bg-white p-3 rounded-xl border text-center">
                      <span className="text-[11px] text-gray-500 uppercase font-semibold">Pump Runtime</span>
                      <div className="text-lg font-black text-purple-700 mt-0.5">{simResult.pump_runtime?.formatted}</div>
                      <span className="text-[10px] text-gray-400">@{simParams.pump_hp} HP</span>
                    </div>
                    <div className="bg-white p-3 rounded-xl border text-center">
                      <span className="text-[11px] text-gray-500 uppercase font-semibold">Power Used</span>
                      <div className="text-lg font-black text-amber-700 mt-0.5">{simResult.pump_runtime?.energy_kwh} kWh</div>
                      <span className="text-[10px] text-gray-400">Energy est.</span>
                    </div>
                  </div>
                </div>

                {/* Agronomic Transparency & Formula Breakdown */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border space-y-4">
                  <h4 className="font-bold text-gray-900 text-sm flex items-center">
                    <Info className="w-4 h-4 text-blue-600 mr-2" />
                    Mathematical & Hydrodynamic Breakdown (FAO-56)
                  </h4>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Ref. Evapotranspiration (ET0)</span>
                      <div className="font-bold text-slate-800 text-sm mt-1">{simResult.reference_et0_mm_day} mm/day</div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Crop Coeff. (Kc × ET0 = ETc)</span>
                      <div className="font-bold text-slate-800 text-sm mt-1">{simResult.crop_coefficient_kc} (ETc: {simResult.crop_etc_mm_day} mm)</div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Effective Rain (Peff Credit)</span>
                      <div className="font-bold text-emerald-700 text-sm mt-1">-{simResult.effective_rainfall_mm} mm</div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Soil Field Capacity (FC)</span>
                      <div className="font-bold text-slate-800 text-sm mt-1">{simResult.field_capacity_pct}% (PWP: {simResult.wilting_point_pct}%)</div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Root Zone Depth</span>
                      <div className="font-bold text-slate-800 text-sm mt-1">{simResult.root_depth_cm} cm (RAW: {simResult.readily_available_water_mm} mm)</div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-gray-500">Application Efficiency</span>
                      <div className="font-bold text-slate-800 text-sm mt-1">{simResult.system_efficiency_pct}% ({simResult.irrigation_method})</div>
                    </div>
                  </div>

                  {simResult.alerts?.length > 0 && (
                    <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 space-y-1 mt-2">
                      <span className="font-bold flex items-center text-amber-800">
                        <AlertTriangle className="w-3.5 h-3.5 mr-1" />
                        Agro-Advisory Risk Alerts:
                      </span>
                      {simResult.alerts.map((a, i) => (
                        <p key={i}>• {a}</p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Farmer Multi-Language Bulletin Card */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-gray-900 text-sm flex items-center">
                      <BookOpen className="w-4 h-4 text-purple-600 mr-2" />
                      Farmer Advisory Bulletin (Multi-Language)
                    </h4>
                    <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg text-xs font-semibold">
                      <button
                        onClick={() => setBulletinLang('en')}
                        className={`px-2.5 py-1 rounded-md ${bulletinLang === 'en' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                      >
                        English
                      </button>
                      <button
                        onClick={() => setBulletinLang('hi')}
                        className={`px-2.5 py-1 rounded-md ${bulletinLang === 'hi' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                      >
                        हिंदी
                      </button>
                      <button
                        onClick={() => setBulletinLang('te')}
                        className={`px-2.5 py-1 rounded-md ${bulletinLang === 'te' ? 'bg-white shadow text-blue-600' : 'text-gray-600'}`}
                      >
                        తెలుగు
                      </button>
                    </div>
                  </div>

                  <div className="p-4 bg-purple-50/50 rounded-xl border border-purple-100 text-sm text-purple-950 font-medium leading-relaxed">
                    {simResult.bulletins?.[bulletinLang]}
                  </div>

                  <div className="flex justify-end space-x-3 pt-2">
                    <button
                      onClick={handleCopyBulletin}
                      className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-semibold rounded-lg transition flex items-center space-x-1"
                    >
                      {copiedBulletin ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedBulletin ? 'Copied to Clipboard!' : 'Copy Bulletin'}</span>
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white p-12 rounded-2xl border text-center text-gray-500">
                Adjust parameters on the left to calculate live advisory.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* TAB 3: 7-DAY PREDICTIVE IRRIGATION SCHEDULE                         */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {activeTab === 'schedule' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 flex items-center">
                  <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                  7-Day Projected Soil Moisture & Irrigation Schedule
                </h2>
                <p className="text-xs text-gray-500 mt-1">
                  Projected forward using daily crop evapotranspiration (<span className="font-mono">ETc</span>) decay and forecast rainfall recharge.
                </p>
              </div>

              <div className="flex items-center space-x-2 text-xs">
                <span className="px-2.5 py-1 bg-blue-50 text-blue-700 font-bold rounded-lg border border-blue-200">
                  {simParams.crop_type} ({simParams.growth_stage})
                </span>
                <span className="px-2.5 py-1 bg-gray-50 text-gray-700 font-bold rounded-lg border">
                  {simParams.soil_type}
                </span>
              </div>
            </div>

            {/* Schedule Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="bg-gray-50 text-gray-600 text-xs uppercase font-bold border-y">
                    <th className="py-3.5 px-4">Day</th>
                    <th className="py-3.5 px-4">Weather Forecast</th>
                    <th className="py-3.5 px-4">Daily ETc Loss</th>
                    <th className="py-3.5 px-4">Effective Rain</th>
                    <th className="py-3.5 px-4">Projected Moisture</th>
                    <th className="py-3.5 px-4">Advisory Action</th>
                    <th className="py-3.5 px-4">Water Required</th>
                    <th className="py-3.5 px-4">Pump Run</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {simSchedule.map((day) => {
                    const isIrrigate = day.action === 'IRRIGATE';
                    return (
                      <tr key={day.day} className={`hover:bg-gray-50/80 transition ${isIrrigate ? 'bg-blue-50/30' : ''}`}>
                        <td className="py-3.5 px-4 font-bold text-gray-900 whitespace-nowrap">
                          {day.date}
                          <span className="block text-[11px] text-gray-400 font-normal">Day {day.day}</span>
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            {day.rain_prob_pct > 30 ? (
                              <CloudRain className="w-4 h-4 text-blue-500" />
                            ) : (
                              <Sun className="w-4 h-4 text-amber-500" />
                            )}
                            <span className="font-medium text-gray-800">{day.temp_c}°C</span>
                            <span className="text-xs text-gray-500">({day.rain_prob_pct}% rain)</span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-rose-600 font-bold whitespace-nowrap">
                          -{day.crop_etc_mm} mm
                        </td>
                        <td className="py-3.5 px-4 text-emerald-600 font-bold whitespace-nowrap">
                          {day.effective_rain_mm > 0 ? `+${day.effective_rain_mm} mm` : '0 mm'}
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            <span className={`font-bold ${day.projected_moisture_pct < day.threshold_pct ? 'text-amber-600' : 'text-emerald-600'}`}>
                              {day.projected_moisture_pct}%
                            </span>
                            <div className="w-16 bg-gray-200 rounded-full h-1.5 hidden sm:block">
                              <div
                                className={`h-1.5 rounded-full ${day.projected_moisture_pct < day.threshold_pct ? 'bg-amber-500' : 'bg-emerald-500'}`}
                                style={{ width: `${Math.min(100, (day.projected_moisture_pct / 70) * 100)}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <span
                            className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                              isIrrigate
                                ? 'bg-blue-600 text-white'
                                : day.action === 'WAIT'
                                ? 'bg-indigo-100 text-indigo-800'
                                : 'bg-emerald-100 text-emerald-800'
                            }`}
                          >
                            {day.action}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-extrabold text-blue-700 whitespace-nowrap">
                          {day.water_mm > 0 ? `${day.water_mm} mm (${day.water_litres.toLocaleString()} L)` : '—'}
                        </td>
                        <td className="py-3.5 px-4 text-slate-700 font-medium whitespace-nowrap">
                          {day.pump_runtime !== '0 min' ? day.pump_runtime : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* TAB 4: CROP AGRONOMIC GUIDE & KC REFERENCE                           */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {activeTab === 'agronomy' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border">
            <div className="border-b pb-4 mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <BookOpen className="w-5 h-5 text-indigo-600 mr-2" />
                FAO-56 Agronomic Crop Coefficients & Water Demand Directory
              </h2>
              <p className="text-xs text-gray-500 mt-1">
                Calibrated crop coefficients (<span className="font-mono">Kc</span>), daily transpiration needs, soil moisture thresholds, and root depth.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="bg-gray-50 text-gray-600 text-xs uppercase font-bold border-y">
                    <th className="py-3.5 px-4">Crop</th>
                    <th className="py-3.5 px-4">Stage</th>
                    <th className="py-3.5 px-4">Kc Coeff.</th>
                    <th className="py-3.5 px-4">Water Demand (mm/day)</th>
                    <th className="py-3.5 px-4">Moisture Threshold (%)</th>
                    <th className="py-3.5 px-4">Root Depth (cm)</th>
                    <th className="py-3.5 px-4">Depletion (p)</th>
                    <th className="py-3.5 px-4">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {cropsList.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/80 transition">
                      <td className="py-3.5 px-4 font-bold text-gray-900">{item.crop_type}</td>
                      <td className="py-3.5 px-4 text-gray-700 font-medium">{item.growth_stage}</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-purple-700">{item.kc?.toFixed(2)}</td>
                      <td className="py-3.5 px-4 font-bold text-blue-700">{item.water_requirement_mm_per_day} mm/d</td>
                      <td className="py-3.5 px-4 font-bold text-emerald-700">{item.moisture_threshold_percent}%</td>
                      <td className="py-3.5 px-4 text-slate-600">{item.root_depth_cm} cm</td>
                      <td className="py-3.5 px-4 text-slate-600">{item.depletion_p}</td>
                      <td className="py-3.5 px-4 text-gray-500">{item.stage_days || 30} days</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
