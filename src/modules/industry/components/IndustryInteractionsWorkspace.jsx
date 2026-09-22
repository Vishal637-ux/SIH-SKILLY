import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Calendar, Plus, Video, Users, CheckCircle, AlertTriangle, X } from 'lucide-react';

export default function IndustryInteractionsWorkspace() {
  const [interactions, setInteractions] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    opportunity_id: '',
    interaction_type: 'INTERVIEW',
    title: '',
    scheduled_at: '',
    meeting_link: '',
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [intRes, oppRes] = await Promise.all([
        api.get('/api/v1/industry/interactions'),
        api.get('/api/v1/industry/opportunities'),
      ]);
      setInteractions(intRes.data || []);
      const opps = oppRes.data.opportunities || [];
      setOpportunities(opps);
      if (opps.length > 0) {
        setForm((prev) => ({ ...prev, opportunity_id: opps[0].id }));
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load placement interactions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
      };
      await api.post('/api/v1/industry/interactions', payload);
      setShowModal(false);
      setForm({
        opportunity_id: opportunities[0]?.id || '',
        interaction_type: 'INTERVIEW',
        title: '',
        scheduled_at: '',
        meeting_link: '',
      });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to schedule interaction.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading label="Loading scheduled recruitment interactions..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Recruitment & Campus Drive Interactions</h2>
          <p className="text-xs text-slate-500">Schedule technical interviews, group discussions, tests, and campus drive events</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setShowModal(true)} disabled={opportunities.length === 0}>
          <Plus className="w-4 h-4 mr-1.5" />
          Schedule Interaction
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{error}</p>
        </div>
      )}

      {/* Interactions List */}
      {interactions.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center max-w-md mx-auto space-y-2">
          <Calendar className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No scheduled interactions</h3>
          <p className="text-xs text-slate-500">Schedule interviews or campus drives to connect with candidates.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {interactions.map((pi) => (
            <div key={pi.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 text-[10px] font-extrabold">
                  {pi.interaction_type}
                </span>
                <span className="text-[11px] text-slate-500 font-semibold">
                  {new Date(pi.scheduled_at).toLocaleString()}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">{pi.title}</h3>
                <p className="text-xs text-slate-600">Opportunity: {pi.opportunity_title}</p>
              </div>

              {pi.meeting_link && (
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Video className="w-3.5 h-3.5 text-blue-600" /> Virtual Link Available
                  </span>
                  <a
                    href={pi.meeting_link}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600 font-bold hover:underline"
                  >
                    Join Meeting &rarr;
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="text-base font-bold text-slate-900">Schedule Recruitment Interaction</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Target Opportunity *</label>
                <select
                  value={form.opportunity_id}
                  onChange={(e) => setForm({ ...form, opportunity_id: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {opportunities.map((opp) => (
                    <option key={opp.id} value={opp.id}>
                      {opp.title} ({opp.location})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Interaction Type *</label>
                <select
                  value={form.interaction_type}
                  onChange={(e) => setForm({ ...form, interaction_type: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="INTERVIEW">Technical Interview</option>
                  <option value="GD">Group Discussion (GD)</option>
                  <option value="TEST">Online Assessment / Test</option>
                  <option value="CAMPUS_DRIVE">Campus Placement Drive</option>
                  <option value="WORKSHOP">Technical Workshop</option>
                  <option value="GUEST_LECTURE">Guest Lecture</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Interaction Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Technical Round 1 - Coding & Architecture"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Scheduled Date & Time *</label>
                <input
                  type="datetime-local"
                  required
                  value={form.scheduled_at}
                  onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Meeting Link (Optional)</label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/xyz"
                  value={form.meeting_link}
                  onChange={(e) => setForm({ ...form, meeting_link: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-200">
                <Button type="button" variant="outline" size="sm" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={submitting}>
                  {submitting ? 'Scheduling...' : 'Confirm Schedule'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
