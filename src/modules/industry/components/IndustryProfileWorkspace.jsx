import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Building2, Save, X, AlertTriangle, CheckCircle, Globe, MapPin, Users, Mail } from 'lucide-react';

export default function IndustryProfileWorkspace() {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/api/v1/industry/profile');
      setProfile(res.data);
      setFormData({
        name: res.data.name || '',
        industry_type: res.data.industry_type || '',
        company_size: res.data.company_size || '',
        website: res.data.website || '',
        logo_url: res.data.logo_url || '',
        headquarters: res.data.headquarters || '',
        description: res.data.description || '',
        designation: res.data.user_designation || '',
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load company profile.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const res = await api.put('/api/v1/industry/profile', formData);
      setProfile(res.data);
      setSuccessMsg('Corporate profile updated successfully!');
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update company profile.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (profile) {
      setFormData({
        name: profile.name || '',
        industry_type: profile.industry_type || '',
        company_size: profile.company_size || '',
        website: profile.website || '',
        logo_url: profile.logo_url || '',
        headquarters: profile.headquarters || '',
        description: profile.description || '',
        designation: profile.user_designation || '',
      });
      setError(null);
      setSuccessMsg(null);
    }
  };

  if (loading) {
    return <Loading label="Loading corporate profile..." />;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Alert Notices */}
      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{successMsg}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{error}</p>
        </div>
      )}

      {/* Corporate Profile Card */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="bg-slate-50 border-b border-slate-200 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">{profile.name}</h2>
              <p className="text-xs text-slate-500">Corporate Identity & Employer Information</p>
            </div>
          </div>
          <div className="text-right">
            <span className="px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold rounded-full">
              {profile.user_hr_role}
            </span>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Main Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Company Legal Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Industry Sector *</label>
              <input
                type="text"
                name="industry_type"
                value={formData.industry_type}
                onChange={handleChange}
                required
                placeholder="e.g. Software & Technology, Healthcare, Finance"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Company Size</label>
              <select
                name="company_size"
                value={formData.company_size}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Company Size</option>
                <option value="1-10 employees">1-10 employees</option>
                <option value="10-50 employees">10-50 employees</option>
                <option value="50-200 employees">50-200 employees</option>
                <option value="200-500 employees">200-500 employees</option>
                <option value="500-1000 employees">500-1000 employees</option>
                <option value="1000+ employees">1000+ employees</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Headquarters Location</label>
              <input
                type="text"
                name="headquarters"
                value={formData.headquarters}
                onChange={handleChange}
                placeholder="e.g. San Francisco, CA / Bengaluru, India"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Corporate Website URL</label>
              <input
                type="url"
                name="website"
                value={formData.website}
                onChange={handleChange}
                placeholder="https://company.example.com"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Logo URL</label>
              <input
                type="url"
                name="logo_url"
                value={formData.logo_url}
                onChange={handleChange}
                placeholder="https://company.example.com/logo.png"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Company Overview & Culture</label>
            <textarea
              name="description"
              rows={4}
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe your company's mission, engineering stack, work culture, and career opportunities..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-xs font-bold text-slate-900 mb-3">Recruiter Personal Contact Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Your Recruiter Designation *</label>
                <input
                  type="text"
                  name="designation"
                  value={formData.designation}
                  onChange={handleChange}
                  required
                  placeholder="e.g. Senior Recruiter, Hiring Lead"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 mb-1">Account Email (Immutable)</label>
                <input
                  type="email"
                  value={profile.user_email}
                  disabled
                  className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-500 cursor-not-allowed"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="bg-slate-50 border-t border-slate-200 p-4 flex justify-end gap-3">
          <Button type="button" variant="outline" size="sm" onClick={handleCancel}>
            <X className="w-3.5 h-3.5 mr-1" />
            Cancel Changes
          </Button>
          <Button type="submit" variant="primary" size="sm" disabled={saving}>
            <Save className="w-3.5 h-3.5 mr-1" />
            {saving ? 'Saving...' : 'Save Profile Changes'}
          </Button>
        </div>
      </form>
    </div>
  );
}
