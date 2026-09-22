import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Users, 
  Briefcase, 
  TrendingUp, 
  Award, 
  AlertTriangle,
  RefreshCw,
  Layers,
  ChevronRight
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function CollegeDashboardWorkspace() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/college/dashboard');
      setDashboard(res.data);
    } catch (err) {
      console.error('Failed to load college dashboard:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load college dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <Loading message="Loading institutional TPO dashboard metrics..." />;
  }

  if (errorMsg) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-lg font-bold text-red-900">Dashboard Access Error</h3>
        <p className="text-sm text-red-700">{errorMsg}</p>
        <Button onClick={fetchDashboard} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-1.5" />
          <span>Retry</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-slate-900 to-indigo-950 rounded-2xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-400/30">
              <Building2 className="w-3.5 h-3.5" />
              <span>{dashboard?.institution_name || 'Institutional Portal'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">TPO Placement & Skill Intelligence</h1>
            <p className="text-sm text-indigo-200/90 max-w-2xl">
              Real-time campus placement statistics, department skill-gap heatmaps, and candidate shortlisting engine.
            </p>
          </div>
          <Button onClick={fetchDashboard} variant="white" size="sm" icon={<RefreshCw className="w-4 h-4" />}>
            Refresh Metrics
          </Button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Enrolled</span>
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900">{dashboard?.total_students || 0}</div>
            <p className="text-xs text-slate-500 mt-1">Across {dashboard?.total_departments || 0} Departments</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Placement Rate</span>
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900">{dashboard?.placement_rate_percentage || 0}%</div>
            <p className="text-xs text-emerald-600 font-medium mt-1">{dashboard?.total_placements || 0} Confirmed Offers</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Package</span>
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Award className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900">₹{dashboard?.average_package_lpa || 0} LPA</div>
            <p className="text-xs text-slate-500 mt-1">Highest: ₹{dashboard?.highest_package_lpa || 0} LPA</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Campus Drives</span>
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900">{dashboard?.active_drives || 0}</div>
            <p className="text-xs text-amber-700 font-medium mt-1">Open Industry Postings</p>
          </div>
        </div>
      </div>

      {/* Critical Skill Gaps Section */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Critical Institutional Skill Gaps</h3>
            <p className="text-xs text-slate-500">Top technical & domain skills with highest student gap frequency across batches.</p>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">Live Analytics</span>
        </div>

        {dashboard?.top_skill_gaps && dashboard.top_skill_gaps.length > 0 ? (
          <div className="space-y-4">
            {dashboard.top_skill_gaps.map((item, idx) => (
              <div key={item.skill_id} className="p-4 rounded-xl bg-slate-50 border border-slate-200/60 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center">
                    #{idx + 1}
                  </span>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900">{item.skill_name}</h4>
                    <span className="text-xs text-slate-500">Identified in batch assessment profiles</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-indigo-600">{item.student_count} Students</span>
                  <p className="text-xs text-slate-400">Require training & gap closure</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 text-sm">
            No institutional skill gaps recorded yet. As students take assessments, batch gaps will aggregate here.
          </div>
        )}
      </div>
    </div>
  );
}
