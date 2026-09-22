import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Briefcase, Plus, Search, MapPin, Calendar, Users, X, CheckCircle, AlertTriangle, Power } from 'lucide-react';

export default function IndustryOpportunitiesWorkspace() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  // Form state for creating opportunity
  const [form, setForm] = useState({
    title: '',
    role_type: 'FULL_TIME',
    description: '',
    location: '',
    is_remote: false,
    stipend_salary: '',
    duration_months: 12,
    openings_count: 1,
    application_deadline: '',
  });

  const fetchOpportunities = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/industry/opportunities');
      setOpportunities(res.data.opportunities || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load opportunities.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleCreateOpportunity = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        duration_months: form.duration_months ? parseInt(form.duration_months, 10) : null,
        openings_count: parseInt(form.openings_count, 10) || 1,
        application_deadline: new Date(form.application_deadline).toISOString(),
      };
      await api.post('/api/v1/industry/opportunities', payload);
      setShowModal(false);
      setForm({
        title: '',
        role_type: 'FULL_TIME',
        description: '',
        location: '',
        is_remote: false,
        stipend_salary: '',
        duration_months: 12,
        openings_count: 1,
        application_deadline: '',
      });
      fetchOpportunities();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create opportunity.');
    } finally {
      setSaving(false);
    }
  };

  const handleCloseOpportunity = async (id) => {
    if (!window.confirm('Are you sure you want to close this opportunity?')) return;
    try {
      await api.delete(`/api/v1/industry/opportunities/${id}`);
      fetchOpportunities();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to close opportunity.');
    }
  };

  if (loading) {
    return <Loading label="Loading company opportunities..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Job & Internship Postings</h2>
          <p className="text-xs text-slate-500">Manage corporate postings, eligibility requirements, and deadlines</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => setShowModal(true)}>
          <Plus className="w-4 h-4 mr-1.5" />
          Post New Opportunity
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{error}</p>
        </div>
      )}

      {/* Opportunities List */}
      {opportunities.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center max-w-lg mx-auto space-y-3">
          <Briefcase className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No active postings</h3>
          <p className="text-xs text-slate-500">Create your first job or internship opportunity to start receiving candidate applications.</p>
          <Button variant="primary" size="sm" onClick={() => setShowModal(true)}>
            Post Opportunity Now
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {opportunities.map((opp) => (
            <div key={opp.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3 hover:shadow-md transition">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold">
                      {opp.role_type}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      opp.status === 'OPEN' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {opp.status}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900">{opp.title}</h3>
                </div>
                {opp.status === 'OPEN' && (
                  <button
                    onClick={() => handleCloseOpportunity(opp.id)}
                    title="Close Opportunity"
                    className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-slate-50 transition"
                  >
                    <Power className="w-4 h-4" />
                  </button>
                )}
              </div>

              <p className="text-xs text-slate-600 line-clamp-2">{opp.description}</p>

              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500 pt-2 border-t border-slate-100">
                <div className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>{opp.location} {opp.is_remote ? '(Remote)' : ''}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-3.5 h-3.5 text-slate-400" />
                  <span>{opp.openings_count} Openings</span>
                </div>
                <div className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                  <span>{opp.stipend_salary || 'Competitive'}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  <span>Deadline: {new Date(opp.application_deadline).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">
                  {opp.applications_count} Candidate Applications
                </span>
                <span className="text-xs font-bold text-blue-600 hover:underline">
                  Manage ATS &rarr;
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Post Opportunity Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="text-base font-bold text-slate-900">Post New Opportunity</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateOpportunity} className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Position Title *</label>
                <input
                  type="text"
                  name="title"
                  value={form.title}
                  onChange={handleFormChange}
                  required
                  placeholder="e.g. Full Stack Developer, Data Analyst Intern"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Role Type *</label>
                  <select
                    name="role_type"
                    value={form.role_type}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="FULL_TIME">FULL TIME</option>
                    <option value="INTERNSHIP">INTERNSHIP</option>
                    <option value="PART_TIME">PART TIME</option>
                    <option value="PROJECT">PROJECT</option>
                    <option value="CONTRACT">CONTRACT</option>
                  </select>
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Location *</label>
                  <input
                    type="text"
                    name="location"
                    value={form.location}
                    onChange={handleFormChange}
                    required
                    placeholder="e.g. Bangalore / Mumbai"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Stipend / Salary Range</label>
                  <input
                    type="text"
                    name="stipend_salary"
                    value={form.stipend_salary}
                    onChange={handleFormChange}
                    placeholder="e.g. 12 LPA or 25,000/mo"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Openings Count</label>
                  <input
                    type="number"
                    name="openings_count"
                    min="1"
                    value={form.openings_count}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Application Deadline *</label>
                  <input
                    type="date"
                    name="application_deadline"
                    value={form.application_deadline}
                    onChange={handleFormChange}
                    required
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center pt-5">
                  <label className="flex items-center gap-2 cursor-pointer font-semibold text-slate-700">
                    <input
                      type="checkbox"
                      name="is_remote"
                      checked={form.is_remote}
                      onChange={handleFormChange}
                      className="rounded text-blue-600 focus:ring-blue-500 h-4 w-4"
                    />
                    <span>Work From Home / Remote</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Role Description & Responsibilities *</label>
                <textarea
                  name="description"
                  rows={4}
                  value={form.description}
                  onChange={handleFormChange}
                  required
                  placeholder="Outline key responsibilities, required qualifications, and candidate benefits..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-200">
                <Button type="button" variant="outline" size="sm" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={saving}>
                  {saving ? 'Publishing...' : 'Publish Opportunity'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
