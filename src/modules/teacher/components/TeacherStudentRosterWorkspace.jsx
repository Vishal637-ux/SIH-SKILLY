import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Search, GraduationCap, Users, AlertCircle } from 'lucide-react';

export default function TeacherStudentRosterWorkspace() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [semester, setSemester] = useState('');
  const [page, setPage] = useState(1);

  const fetchRoster = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page, limit: 10 };
      if (search) params.search = search;
      if (semester) params.current_semester = parseInt(semester, 10);

      const res = await api.get('/api/v1/teacher/students', { params });
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load department student roster.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoster();
  }, [page, semester]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchRoster();
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-indigo-600" />
              <span>Department Student Roster</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Read-only academic monitoring for students in your assigned department.
            </p>
          </div>

          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Roll # or Name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 pr-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none w-48"
              />
            </div>

            <select
              value={semester}
              onChange={(e) => { setSemester(e.target.value); setPage(1); }}
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="">All Semesters</option>
              {[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
                <option key={sem} value={sem}>Semester {sem}</option>
              ))}
            </select>

            <button
              type="submit"
              className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
            >
              Search
            </button>
          </form>
        </div>
      </div>

      {loading ? (
        <Loading label="Loading department student roster..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : !data || data.students.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200/80 shadow-sm text-center">
          <GraduationCap className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-700">No students found</p>
          <p className="text-xs text-slate-500 mt-1">No student records match the active department filters.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-[11px] uppercase tracking-wider font-semibold border-b border-slate-200">
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4">Semester</th>
                  <th className="py-3 px-4">Graduation Year</th>
                  <th className="py-3 px-4">CGPA</th>
                  <th className="py-3 px-4">Target Career Goal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {data.students.map((st) => (
                  <tr key={st.student_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-indigo-700">{st.roll_number}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">{st.first_name} {st.last_name}</td>
                    <td className="py-3.5 px-4">Sem {st.current_semester}</td>
                    <td className="py-3.5 px-4">{st.graduation_year}</td>
                    <td className="py-3.5 px-4">
                      {st.cgpa ? (
                        <span className={`px-2 py-0.5 rounded font-bold ${
                          parseFloat(st.cgpa) >= 8.0
                            ? 'bg-emerald-100 text-emerald-800'
                            : parseFloat(st.cgpa) >= 6.0
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {st.cgpa}
                        </span>
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {st.target_career_role ? (
                        <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium text-[11px]">
                          {st.target_career_role}
                        </span>
                      ) : (
                        <span className="text-slate-400 italic">Not set</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Showing page {data.page} (Total {data.total} students)</span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1 rounded bg-slate-100 disabled:opacity-50 font-semibold hover:bg-slate-200 transition"
              >
                Previous
              </button>
              <button
                disabled={page * 10 >= data.total}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1 rounded bg-slate-100 disabled:opacity-50 font-semibold hover:bg-slate-200 transition"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
