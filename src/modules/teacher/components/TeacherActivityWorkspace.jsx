import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Calendar, Plus, MapPin, X, AlertCircle } from 'lucide-react';

export default function TeacherActivityWorkspace() {
  const [activities, setActivities] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scope, setScope] = useState('institution');

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    title: '',
    description: '',
    activity_type: 'GUEST_LECTURE',
    start_time: '',
    end_time: '',
    location_or_url: ''
  });
  const [msg, setMsg] = useState({ type: '', text: '' });

  const fetchActivities = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/teacher/activities', {
        params: { scope, page: 1, limit: 20 }
      });
      setActivities(res.data.activities);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load activities.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [scope]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg({ type: '', text: '' });
    try {
      const payload = {
        title: form.title,
        description: form.description,
        activity_type: form.activity_type,
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
        location_or_url: form.location_or_url || null
      };

      await api.post('/api/v1/teacher/activities', payload);
      setShowModal(false);
      setForm({ title: '', description: '', activity_type: 'GUEST_LECTURE', start_time: '', end_time: '', location_or_url: '' });
      fetchActivities();
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to schedule activity.' });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <span>Campus & Department Activities</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Schedule industry guest lectures, webinars, and campus workshops.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            <option value="institution">All Institution Activities</option>
            <option value="my_activities">My Conducted Activities</option>
          </select>

          <Button variant="primary" size="sm" onClick={() => setShowModal(true)}>
            <Plus className="w-4 h-4 mr-1" />
            <span>Schedule Activity</span>
          </Button>
        </div>
      </div>

      {loading ? (
        <Loading label="Loading activities..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      ) : activities.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200/80 shadow-sm text-center">
          <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-semibold text-slate-700">No activities scheduled</p>
          <p className="text-xs text-slate-500 mt-1">Schedule an industry guest lecture or webinar.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {activities.map((act) => (
            <div key={act.id} className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-[10px] font-bold">
                  {act.activity_type}
                </span>
                {act.conducted_by_name && (
                  <span className="text-[11px] text-slate-400 font-medium">
                    Presenter: {act.conducted_by_name}
                  </span>
                )}
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">{act.title}</h3>
                <p className="text-xs text-slate-600 mt-1 line-clamp-2">{act.description}</p>
              </div>

              <div className="pt-2 border-t border-slate-100 space-y-1 text-xs text-slate-500">
                <p>Time: {new Date(act.start_time).toLocaleString()} to {new Date(act.end_time).toLocaleTimeString()}</p>
                {act.location_or_url && (
                  <p className="flex items-center gap-1 text-slate-700 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{act.location_or_url}</span>
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Schedule Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm">Schedule Campus Activity / Guest Lecture</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {msg.text && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs font-semibold">
                {msg.text}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Industry Guest Lecture on DevOps"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Activity Type *</label>
                <select
                  value={form.activity_type}
                  onChange={(e) => setForm({ ...form, activity_type: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="GUEST_LECTURE">GUEST_LECTURE</option>
                  <option value="WEBINAR">WEBINAR</option>
                  <option value="WORKSHOP">WORKSHOP</option>
                  <option value="CAMPUS_EVENT">CAMPUS_EVENT</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Description *</label>
                <textarea
                  required
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Start Time *</label>
                  <input
                    type="datetime-local"
                    required
                    value={form.start_time}
                    onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">End Time *</label>
                  <input
                    type="datetime-local"
                    required
                    value={form.end_time}
                    onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Location or Meeting Link</label>
                <input
                  type="text"
                  placeholder="e.g. Seminar Hall A or https://meet.google.com/..."
                  value={form.location_or_url}
                  onChange={(e) => setForm({ ...form, location_or_url: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Schedule Activity
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
