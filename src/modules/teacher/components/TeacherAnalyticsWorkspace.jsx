import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { BarChart3, Users, Award, Briefcase, AlertCircle } from 'lucide-react';

export default function TeacherAnalyticsWorkspace() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/teacher/analytics/department');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load department analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) return <Loading label="Loading department analytics..." />;

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center gap-2">
        <AlertCircle className="w-4 h-4" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-emerald-600" />
            <span>Department Academic & Skill Analytics</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Read-only academic performance metrics for {data.department_name}.
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Total Department Students</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.total_students}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <Briefcase className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Placed Students</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.placed_students_count}</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500">Placement Percentage</p>
            <p className="text-2xl font-extrabold text-slate-900">{data.placement_percentage}%</p>
          </div>
        </div>
      </div>

      {/* Analytics Breakdown Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CGPA Distribution */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-3">
            Department Student CGPA Distribution
          </h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">CGPA ≥ 8.00 (Distinction)</span>
              <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold text-xs">
                {data.cgpa_distribution.above_8} Students
              </span>
            </div>

            <div className="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">CGPA 6.00 – 7.99 (Good)</span>
              <span className="px-3 py-1 bg-amber-100 text-amber-800 rounded-full font-bold text-xs">
                {data.cgpa_distribution.between_6_and_8} Students
              </span>
            </div>

            <div className="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">CGPA &lt; 6.00 (Needs Improvement)</span>
              <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-bold text-xs">
                {data.cgpa_distribution.below_6} Students
              </span>
            </div>
          </div>
        </div>

        {/* Top Department Skill Gaps */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-sm border-b border-slate-100 pb-3">
            Top Department Skill Gaps Needed by Industry
          </h3>

          {data.top_skill_gaps.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">No skill gaps recorded.</p>
          ) : (
            <div className="space-y-3">
              {data.top_skill_gaps.map((gap) => (
                <div key={gap.skill_id} className="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <span className="text-xs font-bold text-slate-800">{gap.skill_name}</span>
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full font-bold text-xs">
                    {gap.student_count} Students
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
