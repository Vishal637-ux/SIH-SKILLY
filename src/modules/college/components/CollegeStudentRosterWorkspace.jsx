import React, { useState, useEffect } from 'react';
import { 
  Users, Search, Filter, ChevronLeft, ChevronRight, 
  GraduationCap, Award, BookOpen, AlertCircle, RefreshCw 
} from 'lucide-react';
import api from '../../../lib/api';

export default function CollegeStudentRosterWorkspace() {
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Pagination
  const [departmentId, setDepartmentId] = useState('');
  const [graduationYear, setGraduationYear] = useState('');
  const [minCgpa, setMinCgpa] = useState('');
  const [currentSemester, setCurrentSemester] = useState('');
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [pagination, setPagination] = useState({ total: 0, total_pages: 1 });

  useEffect(() => {
    fetchDepartments();
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [page, departmentId, graduationYear, minCgpa, currentSemester]);

  const fetchDepartments = async () => {
    try {
      const res = await api.get('/college/departments');
      setDepartments(res.data || []);
    } catch (err) {
      console.error("Failed to fetch departments", err);
    }
  };

  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        limit,
        ...(departmentId && { department_id: departmentId }),
        ...(graduationYear && { graduation_year: parseInt(graduationYear) }),
        ...(minCgpa && { min_cgpa: parseFloat(minCgpa) }),
        ...(currentSemester && { current_semester: parseInt(currentSemester) })
      };
      const res = await api.get('/college/students', { params });
      setStudents(res.data.items || []);
      setPagination({
        total: res.data.total,
        total_pages: res.data.total_pages
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch student roster');
    } finally {
      setLoading(false);
    }
  };

  const resetFilters = () => {
    setDepartmentId('');
    setGraduationYear('');
    setMinCgpa('');
    setCurrentSemester('');
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
              <Users className="w-5 h-5 text-indigo-600" />
              Institutional Student Roster
            </h2>
            <p className="text-sm text-slate-500">
              Browse, filter, and analyze enrolled students across departments and batches.
            </p>
          </div>
          <button 
            onClick={fetchStudents}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-2 border-t border-slate-100">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Department</label>
            <select
              value={departmentId}
              onChange={(e) => { setDepartmentId(e.target.value); setPage(1); }}
              className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">All Departments</option>
              {departments.map(d => (
                <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Graduation Year</label>
            <input
              type="number"
              placeholder="e.g. 2025"
              value={graduationYear}
              onChange={(e) => { setGraduationYear(e.target.value); setPage(1); }}
              className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Min CGPA</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="10"
              placeholder="e.g. 7.5"
              value={minCgpa}
              onChange={(e) => { setMinCgpa(e.target.value); setPage(1); }}
              className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Semester</label>
            <select
              value={currentSemester}
              onChange={(e) => { setCurrentSemester(e.target.value); setPage(1); }}
              className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            >
              <option value="">All Semesters</option>
              {[1,2,3,4,5,6,7,8].map(s => (
                <option key={s} value={s}>Semester {s}</option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={resetFilters}
              className="w-full py-2 px-3 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-lg text-sm font-medium transition"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Roster Table */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-100 shadow-sm">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-slate-500 text-sm">Loading student roster...</p>
        </div>
      ) : students.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-100 shadow-sm space-y-3">
          <Users className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-slate-700 font-medium">No Students Found</h3>
          <p className="text-slate-400 text-sm">Try adjusting your filters or search criteria.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase tracking-wider border-b border-slate-100">
                  <th className="py-3 px-4">Student</th>
                  <th className="py-3 px-4">Department / Batch</th>
                  <th className="py-3 px-4">Academic Metric</th>
                  <th className="py-3 px-4">Target Role</th>
                  <th className="py-3 px-4">Skills & Top Gap</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {students.map((student) => (
                  <tr key={student.student_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-slate-900">{student.full_name}</div>
                      <div className="text-xs text-slate-500 font-mono">{student.roll_number || student.email}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="text-slate-800 font-medium">{student.department_name || 'Unassigned'}</div>
                      <div className="text-xs text-slate-500">
                        Class of {student.graduation_year || 'N/A'} • Sem {student.current_semester || 'N/A'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center gap-1 font-semibold px-2.5 py-0.5 rounded-full text-xs ${
                        (student.cgpa || 0) >= 8.0 
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                          : (student.cgpa || 0) >= 6.5 
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        <GraduationCap className="w-3.5 h-3.5" />
                        {student.cgpa != null ? Number(student.cgpa).toFixed(2) : 'N/A'} CGPA
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-xs font-medium bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-md">
                        {student.target_career_role || 'Not set'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="space-y-1">
                        <div className="text-xs text-slate-600">
                          Verified Skills: <span className="font-semibold text-slate-800">{student.skills_count}</span>
                        </div>
                        {student.top_skill_gap && (
                          <div className="text-xs text-rose-600 font-medium flex items-center gap-1">
                            <span>Gap:</span>
                            <span className="bg-rose-50 border border-rose-100 px-1.5 py-0.5 rounded">{student.top_skill_gap}</span>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="px-4 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
            <div className="text-xs text-slate-500">
              Showing page <span className="font-semibold text-slate-700">{page}</span> of{' '}
              <span className="font-semibold text-slate-700">{pagination.total_pages}</span> ({pagination.total} total students)
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="p-1.5 text-slate-600 border border-slate-200 rounded-lg hover:bg-white disabled:opacity-40 disabled:hover:bg-transparent"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= pagination.total_pages}
                onClick={() => setPage(p => p + 1)}
                className="p-1.5 text-slate-600 border border-slate-200 rounded-lg hover:bg-white disabled:opacity-40 disabled:hover:bg-transparent"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
