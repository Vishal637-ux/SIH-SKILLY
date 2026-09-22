import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { BookOpen, Plus, Users, Award, X, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function TeacherTrainingWorkspace() {
  const [programs, setPrograms] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [scope, setScope] = useState('my_programs');
  const [progType, setProgType] = useState('');

  // Create Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    program_type: 'WORKSHOP',
    start_date: '',
    end_date: '',
    capacity: ''
  });
  const [createMsg, setCreateMsg] = useState({ type: '', text: '' });

  // Enrollment Modal State
  const [selectedProg, setSelectedProg] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [loadingEnroll, setLoadingEnroll] = useState(false);
  const [editingEnroll, setEditingEnroll] = useState(null);
  const [enrollForm, setEnrollForm] = useState({
    attendance_percentage: '0.00',
    completion_status: 'ENROLLED',
    certificate_url: ''
  });

  const fetchPrograms = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { scope, page: 1, limit: 20 };
      if (progType) params.program_type = progType;

      const res = await api.get('/api/v1/teacher/training-programs', { params });
      setPrograms(res.data.programs);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load training programs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrograms();
  }, [scope, progType]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setCreateMsg({ type: '', text: '' });
    try {
      const payload = {
        ...createForm,
        capacity: createForm.capacity ? parseInt(createForm.capacity, 10) : null
      };
      await api.post('/api/v1/teacher/training-programs', payload);
      setShowCreateModal(false);
      setCreateForm({ title: '', description: '', program_type: 'WORKSHOP', start_date: '', end_date: '', capacity: '' });
      fetchPrograms();
    } catch (err) {
      setCreateMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to create training program.' });
    }
  };

  const handleOpenEnrollments = async (prog) => {
    setSelectedProg(prog);
    setLoadingEnroll(true);
    setEditingEnroll(null);
    try {
      const res = await api.get(`/api/v1/teacher/training-programs/${prog.id}/enrollments`);
      setEnrollments(res.data.enrollments);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to load enrollments.');
    } finally {
      setLoadingEnroll(false);
    }
  };

  const handleSaveEnrollment = async (enrollmentId) => {
    try {
      await api.put(`/api/v1/teacher/training-programs/${selectedProg.id}/enrollments/${enrollmentId}`, {
        attendance_percentage: parseFloat(enrollForm.attendance_percentage),
        completion_status: enrollForm.completion_status,
        certificate_url: enrollForm.certificate_url || null
      });
      setEditingEnroll(null);
      handleOpenEnrollments(selectedProg);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update student enrollment.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-emerald-600" />
              <span>Training Programs & Workshops</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Create and manage faculty-conducted workshops, bootcamps, and student training programs.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="my_programs">My Conducted Programs</option>
              <option value="institution">All Institution Programs</option>
            </select>

            <select
              value={progType}
              onChange={(e) => setProgType(e.target.value)}
              className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="">All Types</option>
              <option value="WORKSHOP">WORKSHOP</option>
              <option value="BOOTCAMP">BOOTCAMP</option>
              <option value="MASTERCLASS">MASTERCLASS</option>
            </select>

            <Button variant="primary" size="sm" onClick={() => setShowCreateModal(true)}>
              <Plus className="w-4 h-4 mr-1" />
              <span>Create Program</span>
            </Button>
          </div>
        </div>
      </div>

      {loading ? (
        <Loading label="Loading training programs..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : programs.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200/80 shadow-sm text-center">
          <BookOpen className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-700">No training programs found</p>
          <p className="text-xs text-slate-500 mt-1">Click 'Create Program' to schedule a new workshop or bootcamp.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {programs.map((prog) => (
            <div key={prog.id} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                    {prog.program_type}
                  </span>
                  <span className="text-[11px] text-slate-400 font-medium">
                    Conducted by: {prog.conducted_by_name}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{prog.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-2">{prog.description}</p>
                <div className="text-xs text-slate-500 pt-2 flex items-center justify-between border-t border-slate-100">
                  <span>Dates: {prog.start_date} to {prog.end_date}</span>
                  <span className="font-semibold text-indigo-600 flex items-center gap-1">
                    <Users className="w-3.5 h-3.5" />
                    {prog.enrolled_count} Enrolled
                  </span>
                </div>
              </div>

              <div className="pt-2">
                <Button variant="outline" size="sm" onClick={() => handleOpenEnrollments(prog)} className="w-full justify-center">
                  <span>Manage Student Enrollments</span>
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm">Create Training Program / Workshop</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {createMsg.text && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs font-semibold">
                {createMsg.text}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Program Type *</label>
                <select
                  value={createForm.program_type}
                  onChange={(e) => setCreateForm({ ...createForm, program_type: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="WORKSHOP">WORKSHOP</option>
                  <option value="BOOTCAMP">BOOTCAMP</option>
                  <option value="MASTERCLASS">MASTERCLASS</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description *</label>
                <textarea
                  required
                  rows={3}
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Start Date *</label>
                  <input
                    type="date"
                    required
                    value={createForm.start_date}
                    onChange={(e) => setCreateForm({ ...createForm, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">End Date *</label>
                  <input
                    type="date"
                    required
                    value={createForm.end_date}
                    onChange={(e) => setCreateForm({ ...createForm, end_date: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Capacity (Max Students)</label>
                <input
                  type="number"
                  min="1"
                  value={createForm.capacity}
                  onChange={(e) => setCreateForm({ ...createForm, capacity: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Create Program
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Enrollments Modal */}
      {selectedProg && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-2xl w-full space-y-4 shadow-xl max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">{selectedProg.title}</h3>
                <p className="text-xs text-slate-500">Student Enrollments & Attendance</p>
              </div>
              <button onClick={() => setSelectedProg(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {loadingEnroll ? (
              <Loading label="Loading enrollments..." />
            ) : enrollments.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-8">No student enrollments found for this program.</p>
            ) : (
              <div className="space-y-3 divide-y divide-slate-100">
                {enrollments.map((en) => (
                  <div key={en.enrollment_id} className="pt-3 first:pt-0 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-bold text-slate-900">{en.student_name} ({en.roll_number})</p>
                        <p className="text-[11px] text-slate-500">
                          Attendance: <span className="font-semibold text-emerald-600">{en.attendance_percentage}%</span> | Status: <span className="font-semibold">{en.completion_status}</span>
                        </p>
                      </div>

                      {editingEnroll !== en.enrollment_id ? (
                        <button
                          onClick={() => {
                            setEditingEnroll(en.enrollment_id);
                            setEnrollForm({
                              attendance_percentage: en.attendance_percentage,
                              completion_status: en.completion_status,
                              certificate_url: en.certificate_url || ''
                            });
                          }}
                          className="px-2.5 py-1 text-xs font-semibold bg-slate-100 text-slate-700 rounded hover:bg-slate-200 transition"
                        >
                          Update
                        </button>
                      ) : (
                        <button
                          onClick={() => setEditingEnroll(null)}
                          className="px-2.5 py-1 text-xs font-semibold bg-slate-100 text-slate-500 rounded hover:bg-slate-200 transition"
                        >
                          Cancel
                        </button>
                      )}
                    </div>

                    {editingEnroll === en.enrollment_id && (
                      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-3 text-xs">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block font-semibold text-slate-700 mb-1">Attendance %</label>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              max="100"
                              value={enrollForm.attendance_percentage}
                              onChange={(e) => setEnrollForm({ ...enrollForm, attendance_percentage: e.target.value })}
                              className="w-full px-2.5 py-1 border border-slate-300 rounded text-xs"
                            />
                          </div>

                          <div>
                            <label className="block font-semibold text-slate-700 mb-1">Status</label>
                            <select
                              value={enrollForm.completion_status}
                              onChange={(e) => setEnrollForm({ ...enrollForm, completion_status: e.target.value })}
                              className="w-full px-2.5 py-1 border border-slate-300 rounded text-xs bg-white"
                            >
                              <option value="ENROLLED">ENROLLED</option>
                              <option value="ATTENDING">ATTENDING</option>
                              <option value="COMPLETED">COMPLETED</option>
                              <option value="DROPPED">DROPPED</option>
                            </select>
                          </div>
                        </div>

                        <div>
                          <label className="block font-semibold text-slate-700 mb-1">Certificate URL</label>
                          <input
                            type="text"
                            placeholder="https://..."
                            value={enrollForm.certificate_url}
                            onChange={(e) => setEnrollForm({ ...enrollForm, certificate_url: e.target.value })}
                            className="w-full px-2.5 py-1 border border-slate-300 rounded text-xs"
                          />
                        </div>

                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleSaveEnrollment(en.enrollment_id)}
                            className="px-3 py-1 bg-emerald-600 text-white rounded text-xs font-semibold hover:bg-emerald-700 transition"
                          >
                            Save Enrollment Changes
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
