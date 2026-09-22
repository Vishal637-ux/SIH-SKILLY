import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { UserCheck, Calendar, BookOpen, Mail, Award, Plus, X } from 'lucide-react';

export default function AlumniConnectionsWorkspace() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modal state for scheduling session
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [sessionForm, setSessionForm] = useState({
    topic: '',
    scheduled_at: '',
    duration_minutes: 45,
    meeting_link: '',
    session_notes: '',
  });
  const [submittingSession, setSubmittingSession] = useState(false);

  const fetchConnections = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/alumni/connections');
      setConnections(res.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load active mentorship connections.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnections();
  }, []);

  const openScheduleModal = (conn) => {
    setSelectedConnection(conn);
    setSessionForm({
      topic: `Mentorship Session with ${conn.student?.first_name || 'Student'}`,
      scheduled_at: new Date(Date.now() + 86400000 * 2).toISOString().slice(0, 16),
      duration_minutes: 45,
      meeting_link: 'https://meet.google.com/xyz-abc-def',
      session_notes: 'Discussion on career pathway, resume critique, and technical interview prep.',
    });
    setScheduleModalOpen(true);
  };

  const handleScheduleSubmit = async (e) => {
    e.preventDefault();
    setSubmittingSession(true);
    try {
      const payload = {
        connection_id: selectedConnection.id,
        topic: sessionForm.topic,
        scheduled_at: new Date(sessionForm.scheduled_at).toISOString(),
        duration_minutes: parseInt(sessionForm.duration_minutes, 10),
        meeting_link: sessionForm.meeting_link || null,
        session_notes: sessionForm.session_notes || null,
      };

      await api.post('/api/v1/alumni/sessions', payload);
      alert('Mentorship session scheduled successfully!');
      setScheduleModalOpen(false);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to schedule session.');
    } finally {
      setSubmittingSession(false);
    }
  };

  if (loading) {
    return <Loading label="Loading active mentorship connections..." />;
  }

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900">Active Student Mentees</h3>
        <p className="text-xs text-slate-500">Students with accepted mentorship connections under your alumni profile.</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchConnections} className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-semibold">
            Retry
          </button>
        </div>
      )}

      {connections.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center shadow-sm space-y-2">
          <UserCheck className="w-10 h-10 text-slate-300 mx-auto" />
          <h4 className="text-sm font-bold text-slate-700">No active student connections yet</h4>
          <p className="text-xs text-slate-500">Accepted student requests will appear here as active mentees.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {connections.map((conn) => (
            <div key={conn.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-4">
              <div className="flex items-start justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-sm">
                    {conn.student?.first_name?.[0]}{conn.student?.last_name?.[0]}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">
                      {conn.student?.first_name} {conn.student?.last_name}
                    </h4>
                    <p className="text-xs text-slate-500">{conn.student?.email}</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                  CONNECTED
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500 font-medium">Institution & Dept:</span>
                  <span className="text-slate-900 font-semibold">{conn.student?.institution_name || 'N/A'} ({conn.student?.department_name || 'N/A'})</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500 font-medium">Roll Number & Semester:</span>
                  <span className="text-slate-900 font-semibold">{conn.student?.roll_number || 'N/A'} • Sem {conn.student?.current_semester || 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500 font-medium">Academic CGPA:</span>
                  <span className="text-slate-900 font-semibold">{conn.student?.cgpa || 'N/A'} / 10.0</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-50">
                  <span className="text-slate-500 font-medium">Target Career Pathway:</span>
                  <span className="text-purple-700 font-bold">{conn.student?.target_career_role || 'General Mentorship'}</span>
                </div>
                {conn.student?.skills?.length > 0 && (
                  <div className="py-1">
                    <span className="text-slate-500 font-medium block mb-1">Key Student Skills:</span>
                    <div className="flex flex-wrap gap-1">
                      {conn.student.skills.map((skill, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 text-[10px] font-medium border border-purple-100">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => openScheduleModal(conn)}
                  className="px-3.5 py-1.5 bg-purple-700 text-white hover:bg-purple-800 rounded-lg text-xs font-semibold transition shadow-sm flex items-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Schedule Mentorship Session</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Schedule Session Modal */}
      {scheduleModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900">
                Schedule Session for {selectedConnection?.student?.first_name} {selectedConnection?.student?.last_name}
              </h3>
              <button onClick={() => setScheduleModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleScheduleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Session Topic</label>
                <input
                  type="text"
                  required
                  value={sessionForm.topic}
                  onChange={(e) => setSessionForm({ ...sessionForm, topic: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Scheduled Date & Time</label>
                  <input
                    type="datetime-local"
                    required
                    value={sessionForm.scheduled_at}
                    onChange={(e) => setSessionForm({ ...sessionForm, scheduled_at: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Duration (Minutes)</label>
                  <select
                    value={sessionForm.duration_minutes}
                    onChange={(e) => setSessionForm({ ...sessionForm, duration_minutes: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  >
                    <option value={30}>30 Minutes</option>
                    <option value={45}>45 Minutes</option>
                    <option value={60}>60 Minutes</option>
                    <option value={90}>90 Minutes</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Meeting Link (Google Meet / Zoom)</label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/abc-def-ghi"
                  value={sessionForm.meeting_link}
                  onChange={(e) => setSessionForm({ ...sessionForm, meeting_link: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Agenda & Preparation Notes</label>
                <textarea
                  rows={3}
                  value={sessionForm.session_notes}
                  onChange={(e) => setSessionForm({ ...sessionForm, session_notes: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setScheduleModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <Button type="submit" variant="primary" size="md" disabled={submittingSession}>
                  {submittingSession ? 'Scheduling...' : 'Confirm Schedule'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
