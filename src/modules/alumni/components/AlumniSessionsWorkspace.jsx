import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Calendar, Clock, CheckCircle2, XCircle, AlertTriangle, ExternalLink, Filter, Edit3, X } from 'lucide-react';

export default function AlumniSessionsWorkspace() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Edit Modal State
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [updateForm, setUpdateForm] = useState({
    status: 'COMPLETED',
    session_notes: '',
    feedback_rating: 5,
  });
  const [updating, setUpdating] = useState(false);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = statusFilter !== 'ALL' ? `/api/v1/alumni/sessions?status=${statusFilter}` : '/api/v1/alumni/sessions';
      const res = await api.get(endpoint);
      setSessions(res.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load mentorship sessions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [statusFilter]);

  const openUpdateModal = (session) => {
    setSelectedSession(session);
    setUpdateForm({
      status: session.status || 'COMPLETED',
      session_notes: session.session_notes || '',
      feedback_rating: session.feedback_rating || 5,
    });
    setEditModalOpen(true);
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    setUpdating(true);
    try {
      const payload = {
        status: updateForm.status,
        session_notes: updateForm.session_notes || null,
        feedback_rating: updateForm.feedback_rating ? parseInt(updateForm.feedback_rating, 10) : null,
      };

      await api.put(`/api/v1/alumni/sessions/${selectedSession.id}`, payload);
      setEditModalOpen(false);
      await fetchSessions();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update session status.');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <Loading label="Loading mentorship sessions..." />;
  }

  return (
    <div className="space-y-6">
      {/* Workspace Header & Filter */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Mentorship Sessions History & Schedule</h3>
          <p className="text-xs text-slate-500">Track scheduled meetings, launch virtual calls, and record session completion notes.</p>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 bg-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
          >
            <option value="ALL">All Session Statuses</option>
            <option value="SCHEDULED">Scheduled Only</option>
            <option value="COMPLETED">Completed Only</option>
            <option value="CANCELLED">Cancelled Only</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchSessions} className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-semibold">
            Retry
          </button>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center shadow-sm space-y-2">
          <Calendar className="w-10 h-10 text-slate-300 mx-auto" />
          <h4 className="text-sm font-bold text-slate-700">No mentorship sessions found</h4>
          <p className="text-xs text-slate-500">Scheduled mentorship sessions will appear here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((sess) => (
            <div key={sess.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">{sess.topic}</h4>
                  <p className="text-xs text-slate-500">
                    Mentee: {sess.student?.first_name} {sess.student?.last_name} ({sess.student?.email})
                  </p>
                </div>
                <div>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                    sess.status === 'SCHEDULED' ? 'bg-cyan-100 text-cyan-800' :
                    sess.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' :
                    sess.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {sess.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-700 block mb-0.5">Scheduled Date & Time:</span>
                  <span className="text-slate-900 font-medium">{new Date(sess.scheduled_at).toLocaleString()}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block mb-0.5">Session Duration:</span>
                  <span className="text-slate-900 font-medium">{sess.duration_minutes} Minutes</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block mb-0.5">Meeting URL:</span>
                  {sess.meeting_link ? (
                    <a
                      href={sess.meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-600 font-semibold hover:underline flex items-center gap-1"
                    >
                      Join Meeting Call <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-slate-400 italic">No link provided</span>
                  )}
                </div>
              </div>

              {sess.session_notes && (
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs text-slate-700">
                  <span className="font-semibold block mb-0.5 text-slate-900">Session Notes & Agenda:</span>
                  <p>{sess.session_notes}</p>
                </div>
              )}

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => openUpdateModal(sess)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>Update Session Status</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Update Session Status Modal */}
      {editModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900">Update Session Status</h3>
              <button onClick={() => setEditModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Status</label>
                <select
                  value={updateForm.status}
                  onChange={(e) => setUpdateForm({ ...updateForm, status: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                >
                  <option value="SCHEDULED">SCHEDULED</option>
                  <option value="COMPLETED">COMPLETED</option>
                  <option value="CANCELLED">CANCELLED</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Session Notes & Summary</label>
                <textarea
                  rows={4}
                  value={updateForm.session_notes}
                  onChange={(e) => setUpdateForm({ ...updateForm, session_notes: e.target.value })}
                  placeholder="Record session feedback, topics covered, action items for student..."
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updating}
                  className="px-4 py-2 bg-purple-700 text-white hover:bg-purple-800 rounded-lg text-xs font-semibold transition"
                >
                  {updating ? 'Saving...' : 'Update Status'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
