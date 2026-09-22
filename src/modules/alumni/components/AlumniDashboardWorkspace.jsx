import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Users, UserCheck, Calendar, Clock, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function AlumniDashboardWorkspace() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/alumni/dashboard');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load alumni mentor dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <Loading label="Loading mentor workspace dashboard..." />;
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
      {/* Mentor Identity Banner */}
      <div className="bg-gradient-to-r from-purple-800 via-indigo-800 to-slate-900 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-white/20 text-white text-xs font-medium backdrop-blur-sm mb-2">
            <Users className="w-3.5 h-3.5" />
            <span>Alumni Mentor Workspace</span>
          </div>
          <h2 className="text-2xl font-bold">{data.mentor_name}</h2>
          <p className="text-purple-100 text-xs mt-1">Student Mentorship, 1-on-1 Guidance & Career Coaching</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/alumni/requests"
            className="px-4 py-2 bg-white text-purple-900 rounded-xl text-xs font-bold hover:bg-purple-50 transition shadow-sm"
          >
            Review Pending Requests ({data.pending_requests_count})
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Pending Requests</p>
          <p className="text-2xl font-extrabold text-amber-600">{data.pending_requests_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Active Mentees</p>
          <p className="text-2xl font-extrabold text-purple-600">{data.active_connections_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Total Sessions</p>
          <p className="text-2xl font-extrabold text-blue-600">{data.total_sessions_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Upcoming Sessions</p>
          <p className="text-2xl font-extrabold text-cyan-600">{data.scheduled_sessions_count}</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm space-y-1">
          <p className="text-xs font-medium text-slate-500">Completed Sessions</p>
          <p className="text-2xl font-extrabold text-emerald-600">{data.completed_sessions_count}</p>
        </div>
      </div>

      {/* Recent Mentorship Requests Section */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Mentorship Requests</h3>
            <p className="text-xs text-slate-500">Inbound connection requests from registered students</p>
          </div>
          <Link
            to="/alumni/requests"
            className="text-xs font-semibold text-purple-600 hover:text-purple-800 flex items-center gap-1"
          >
            View All Requests <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {data.recent_requests.length === 0 ? (
          <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            <Users className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-700">No mentorship requests yet</p>
            <p className="text-xs text-slate-500">Requests submitted by students will appear here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Student Name</th>
                  <th className="px-4 py-3">Institution & Dept</th>
                  <th className="px-4 py-3">Target Career Role</th>
                  <th className="px-4 py-3">Request Note</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.recent_requests.map((req) => (
                  <tr key={req.id} className="hover:bg-slate-50/50 transition">
                    <td className="px-4 py-3 font-semibold text-slate-900">
                      {req.student?.first_name} {req.student?.last_name}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {req.student?.institution_name || 'N/A'} ({req.student?.department_name || 'N/A'})
                    </td>
                    <td className="px-4 py-3 text-purple-700 font-medium">
                      {req.student?.target_career_role || 'General Mentorship'}
                    </td>
                    <td className="px-4 py-3 text-slate-500 truncate max-w-xs">{req.request_note || 'No note'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        req.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                        req.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                        req.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {req.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to="/alumni/requests"
                        className="text-purple-600 hover:underline font-semibold"
                      >
                        Manage Request
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
