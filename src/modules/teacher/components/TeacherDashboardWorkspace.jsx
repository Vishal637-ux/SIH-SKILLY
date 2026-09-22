import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Users, BookOpen, UserCheck, AlertTriangle, Calendar, Award } from 'lucide-react';

export default function TeacherDashboardWorkspace() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/teacher/dashboard');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load teacher dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <Loading label="Loading teacher dashboard metrics..." />;
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
      {/* Teacher Identity Spotlight */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-white/20 text-white text-xs font-medium backdrop-blur-sm mb-2">
            <span>{data.designation}</span>
            <span>•</span>
            <span>{data.department_name}</span>
          </div>
          <h2 className="text-xl font-bold">{data.institution_name}</h2>
          <p className="text-emerald-100 text-xs mt-1">Academic Department Faculty Portal</p>
        </div>
      </div>

      {/* Top Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Department Students</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.total_department_students}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Programs Conducted</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.programs_conducted_count}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Active Mentorships</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.active_mentorships_count}</p>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Department Skill Gaps */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-600" />
              <span>Department Critical Skill Gaps</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">Top 5 Needs</span>
          </div>

          {data.department_top_skill_gaps.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">No skill gaps recorded for department students.</p>
          ) : (
            <div className="space-y-3">
              {data.department_top_skill_gaps.map((gap) => (
                <div key={gap.skill_id} className="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <span className="text-sm font-semibold text-slate-800">{gap.skill_name}</span>
                  <span className="px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-bold">
                    {gap.student_count} Students Needing Guidance
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Campus Activities */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-600" />
              <span>Recent Department Activities</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">Scheduled</span>
          </div>

          {data.recent_activities.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">No upcoming activities or guest lectures scheduled.</p>
          ) : (
            <div className="space-y-3">
              {data.recent_activities.map((act) => (
                <div key={act.id} className="p-3 bg-slate-50 rounded-lg border border-slate-100 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-slate-900">{act.title}</span>
                    <span className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 text-[10px] font-bold">
                      {act.activity_type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500">
                    {new Date(act.start_time).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
