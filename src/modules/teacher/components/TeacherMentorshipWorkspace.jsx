import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { UserCheck, Check, X, Calendar, MessageSquare, AlertCircle } from 'lucide-react';

export default function TeacherMentorshipWorkspace() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('');

  // Schedule Session Modal State
  const [selectedConn, setSelectedConn] = useState(null);
  const [sessionForm, setSessionForm] = useState({
    topic: '',
    scheduled_at: '',
    duration_minutes: 45,
    meeting_link: '',
    session_notes: ''
  });
  const [sessionMsg, setSessionMsg] = useState({ type: '', text: '' });

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filterStatus) params.status_filter = filterStatus;

      const res = await api.get('/api/v1/teacher/mentorship/requests', { params });
      setRequests(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load mentorship requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [filterStatus]);

  const handleUpdateStatus = async (connectionId, newStatus) => {
    try {
      await api.put(`/api/v1/teacher/mentorship/requests/${connectionId}`, { status: newStatus });
      fetchRequests();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update mentorship status.');
    }
  };

  const handleScheduleSubmit = async (e) => {
    e.preventDefault();
    setSessionMsg({ type: '', text: '' });
    try {
      const payload = {
        connection_id: selectedConn.connection_id,
        topic: sessionForm.topic,
        scheduled_at: new Date(sessionForm.scheduled_at).toISOString(),
        duration_minutes: parseInt(sessionForm.duration_minutes, 10),
        meeting_link: sessionForm.meeting_link || null,
        session_notes: sessionForm.session_notes || null
      };

      await api.post('/api/v1/teacher/mentorship/sessions', payload);
      setSelectedConn(null);
      setSessionForm({ topic: '', scheduled_at: '', duration_minutes: 45, meeting_link: '', session_notes: '' });
      alert('Mentorship session scheduled successfully!');
    } catch (err) {
      setSessionMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to schedule session.' });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-amber-600" />
            <span>Mentorship & Student Guidance</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Review 1-on-1 student mentorship requests, accept connections, and schedule guidance sessions.
          </p>
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-amber-500 focus:outline-none"
        >
          <option value="">All Request Statuses</option>
          <option value="PENDING">PENDING</option>
          <option value="ACCEPTED">ACCEPTED</option>
          <option value="REJECTED">REJECTED</option>
          <option value="COMPLETED">COMPLETED</option>
        </select>
      </div>

      {loading ? (
        <Loading label="Loading mentorship requests..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : requests.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200/80 shadow-sm text-center">
          <UserCheck className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-700">No mentorship requests</p>
          <p className="text-xs text-slate-500 mt-1">Students can request academic guidance from your teacher profile.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {requests.map((req) => (
            <div key={req.connection_id} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{req.student_name}</h3>
                  <p className="text-xs text-slate-500">Roll: {req.student_roll_number} • {req.student_department}</p>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                  req.status === 'ACCEPTED'
                    ? 'bg-emerald-100 text-emerald-800'
                    : req.status === 'PENDING'
                    ? 'bg-amber-100 text-amber-800'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {req.status}
                </span>
              </div>

              {req.request_note && (
                <div className="p-3 bg-slate-50 rounded-lg text-xs text-slate-600 flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                  <p className="italic">"{req.request_note}"</p>
                </div>
              )}

              <div className="pt-2 flex items-center justify-between border-t border-slate-100">
                <span className="text-[11px] text-slate-400">
                  Requested: {new Date(req.created_at).toLocaleDateString()}
                </span>

                <div className="flex items-center gap-2">
                  {req.status === 'PENDING' && (
                    <>
                      <button
                        onClick={() => handleUpdateStatus(req.connection_id, 'REJECTED')}
                        className="p-1.5 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition"
                        title="Reject"
                      >
                        <X className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(req.connection_id, 'ACCEPTED')}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition flex items-center gap-1"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Accept</span>
                      </button>
                    </>
                  )}

                  {req.status === 'ACCEPTED' && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setSelectedConn(req);
                        setSessionForm({ topic: '', scheduled_at: '', duration_minutes: 45, meeting_link: '', session_notes: '' });
                      }}
                    >
                      <Calendar className="w-3.5 h-3.5 mr-1" />
                      <span>Schedule Session</span>
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Schedule Session Modal */}
      {selectedConn && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Schedule Guidance Session</h3>
                <p className="text-xs text-slate-500">Student: {selectedConn.student_name}</p>
              </div>
              <button onClick={() => setSelectedConn(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {sessionMsg.text && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs font-semibold">
                {sessionMsg.text}
              </div>
            )}

            <form onSubmit={handleScheduleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Session Topic / Agenda *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Academic Project Review & Skill Guidance"
                  value={sessionForm.topic}
                  onChange={(e) => setSessionForm({ ...sessionForm, topic: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Date & Time *</label>
                  <input
                    type="datetime-local"
                    required
                    value={sessionForm.scheduled_at}
                    onChange={(e) => setSessionForm({ ...sessionForm, scheduled_at: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Duration (Minutes)</label>
                  <input
                    type="number"
                    min="15"
                    step="15"
                    value={sessionForm.duration_minutes}
                    onChange={(e) => setSessionForm({ ...sessionForm, duration_minutes: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Meeting Link (Google Meet / Zoom)</label>
                <input
                  type="text"
                  placeholder="https://meet.google.com/..."
                  value={sessionForm.meeting_link}
                  onChange={(e) => setSessionForm({ ...sessionForm, meeting_link: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Session Notes / Instructions</label>
                <textarea
                  rows={2}
                  value={sessionForm.session_notes}
                  onChange={(e) => setSessionForm({ ...sessionForm, session_notes: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => setSelectedConn(null)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Schedule Session
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
