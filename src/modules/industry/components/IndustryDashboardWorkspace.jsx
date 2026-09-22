import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Briefcase, Users, UserCheck, Award, Calendar, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function IndustryDashboardWorkspace() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/industry/dashboard');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load industry dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <Loading label="Loading recruiter dashboard..." />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0" />
          <div>
            <p className="font-semibold text-sm">Dashboard Error</p>
            <p className="text-xs text-red-600">{error}</p>
          </div>
        </div>
        <button
          onClick={fetchDashboard}
          className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Identity Spotlight */}
      <div className="bg-gradient-to-r from-blue-700 via-indigo-800 to-slate-900 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-white/20 text-white text-xs font-medium backdrop-blur-sm mb-2">
            <Briefcase className="w-3.5 h-3.5" />
            <span>{data.company_name}</span>
            {data.is_verified && (
              <>
                <span>•</span>
                <span className="text-emerald-300 font-semibold">Verified Employer</span>
              </>
            )}
          </div>
          <h2 className="text-2xl font-bold">{data.company_name} Corporate Workspace</h2>
          <p className="text-blue-100 text-xs mt-1">Recruitment, Candidate Shortlisting & Internship Supervision</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/industry/opportunities"
            className="px-4 py-2 bg-white text-blue-900 rounded-xl text-xs font-bold hover:bg-blue-50 transition shadow-sm"
          >
            Post New Opportunity
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Active Postings</p>
          <p className="text-2xl font-extrabold text-blue-600">{data.active_opportunities_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Total Applicants</p>
          <p className="text-2xl font-extrabold text-slate-900">{data.total_applications_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Shortlisted</p>
          <p className="text-2xl font-extrabold text-amber-600">{data.shortlisted_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Selected / Offered</p>
          <p className="text-2xl font-extrabold text-emerald-600">{data.selected_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Active Interns</p>
          <p className="text-2xl font-extrabold text-purple-600">{data.active_internships_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Interviews Scheduled</p>
          <p className="text-2xl font-extrabold text-cyan-600">{data.upcoming_interactions_count}</p>
        </div>
      </div>

      {/* Recent Applications Section */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Candidate Applications</h3>
            <p className="text-xs text-slate-500">Latest student submissions across your corporate postings</p>
          </div>
          <Link
            to="/industry/applications"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            View All Applications <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {data.recent_applications.length === 0 ? (
          <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <Users className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">No applications received yet</p>
            <p className="text-xs text-slate-500">Applications submitted by students will appear here in real-time.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Candidate Name</th>
                  <th className="px-4 py-3">Opportunity Title</th>
                  <th className="px-4 py-3">Applied Date</th>
                  <th className="px-4 py-3">Current Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.recent_applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/50 transition">
                    <td className="px-4 py-3 font-semibold text-slate-900">{app.student_name}</td>
                    <td className="px-4 py-3 text-slate-700">{app.opportunity_title}</td>
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        app.status === 'APPLIED' ? 'bg-blue-100 text-blue-800' :
                        app.status === 'SHORTLISTED' ? 'bg-amber-100 text-amber-800' :
                        app.status === 'OFFERED' || app.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                        app.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to="/industry/applications"
                        className="text-blue-600 hover:underline font-semibold"
                      >
                        Review ATS
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
