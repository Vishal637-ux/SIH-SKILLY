import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { BarChart3, TrendingUp, Award, Users, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function IndustryAnalyticsWorkspace() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/industry/analytics');
      setAnalytics(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load hiring analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return <Loading label="Calculating corporate hiring analytics..." />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0" />
          <div>
            <p className="font-semibold text-sm">Analytics Error</p>
            <p className="text-xs text-red-600">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchAnalytics}
          className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  const totalFunnelApps = analytics.hiring_funnel.reduce((sum, item) => sum + item.count, 0) || 1;

  return (
    <div className="space-y-6">
      {/* Header Spotlight */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Industry Recruitment Analytics</h2>
          <p className="text-xs text-slate-500">Deterministic SQL metrics for candidate conversion, skill demand, and internship completion</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-xs font-bold">
            {analytics.company_name}
          </span>
        </div>
      </div>

      {/* Top Aggregation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Total Opportunity Postings</p>
          <p className="text-3xl font-extrabold text-blue-600">{analytics.total_postings}</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Total Received Applications</p>
          <p className="text-3xl font-extrabold text-slate-900">{analytics.total_applications}</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Internship Completion Rate</p>
          <p className="text-3xl font-extrabold text-emerald-600">{analytics.internship_completion_rate}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ATS Hiring Funnel Breakdown */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">ATS Hiring Funnel Conversion</h3>
            <p className="text-xs text-slate-500">Candidate distribution across recruitment stages</p>
          </div>

          <div className="space-y-3">
            {analytics.hiring_funnel.map((item) => {
              const pct = Math.round((item.count / totalFunnelApps) * 100);
              return (
                <div key={item.status} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-700">
                    <span>{item.status}</span>
                    <span>{item.count} Candidates ({pct}%)</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        item.status === 'APPLIED' ? 'bg-blue-500' :
                        item.status === 'SHORTLISTED' ? 'bg-amber-500' :
                        item.status === 'INTERVIEWING' ? 'bg-purple-500' :
                        item.status === 'OFFERED' || item.status === 'ACCEPTED' ? 'bg-emerald-500' :
                        'bg-red-400'
                      }`}
                      style={{ width: `${Math.max(pct, 4)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Demanded Required Skills */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Top Required Skills in Postings</h3>
            <p className="text-xs text-slate-500">Most requested technical and professional skills across your opportunities</p>
          </div>

          {analytics.top_demanded_skills.length === 0 ? (
            <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
              <Award className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-600">No required skills attached yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {analytics.top_demanded_skills.map((sk, idx) => (
                <div key={sk.skill_id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-[10px]">
                      #{idx + 1}
                    </span>
                    <span className="font-bold text-slate-900">{sk.skill_name}</span>
                  </div>
                  <span className="px-2.5 py-1 bg-white border border-slate-200 rounded-md text-[10px] font-bold text-slate-700">
                    {sk.postings_count} Postings Tagged
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
