import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import Button from '../../../components/Button';
import { Users, Filter, CheckCircle2, XCircle, Clock, AlertTriangle, FileText, Check, X, User } from 'lucide-react';

export default function IndustryApplicationsWorkspace() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [minCgpa, setMinCgpa] = useState('');
  const [gradYear, setGradYear] = useState('');

  // Selected application for detail / status update
  const [selectedApp, setSelectedApp] = useState(null);
  const [statusHistory, setStatusHistory] = useState([]);
  const [updating, setUpdating] = useState(false);
  const [notesInput, setNotesInput] = useState('');

  const fetchApplications = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = '/api/v1/industry/applications?';
      if (statusFilter) url += `status=${statusFilter}&`;
      if (minCgpa) url += `min_cgpa=${minCgpa}&`;
      if (gradYear) url += `graduation_year=${gradYear}&`;

      const res = await api.get(url);
      setApplications(res.data.applications || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load applicant roster.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [statusFilter, minCgpa, gradYear]);

  const openDetailModal = async (app) => {
    setSelectedApp(app);
    setNotesInput('');
    try {
      const res = await api.get(`/api/v1/industry/applications/${app.id}/history`);
      setStatusHistory(res.data || []);
    } catch (err) {
      setStatusHistory([]);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    if (!selectedApp) return;
    setUpdating(true);
    try {
      const payload = { status: newStatus, notes: notesInput };
      const res = await api.put(`/api/v1/industry/applications/${selectedApp.id}/status`, payload);
      setSelectedApp(res.data);
      // Refresh history
      const histRes = await api.get(`/api/v1/industry/applications/${selectedApp.id}/history`);
      setStatusHistory(histRes.data || []);
      fetchApplications();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update application status.');
    } finally {
      setUpdating(false);
    }
  };

  if (loading && applications.length === 0) {
    return <Loading label="Loading candidate ATS applications..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Applicant Roster & ATS Pipeline</h2>
            <p className="text-xs text-slate-500">Filter, shortlist, and update candidate application stages</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-100 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Status Filter</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="APPLIED">APPLIED</option>
              <option value="SHORTLISTED">SHORTLISTED</option>
              <option value="INTERVIEWING">INTERVIEWING</option>
              <option value="OFFERED">OFFERED</option>
              <option value="REJECTED">REJECTED</option>
              <option value="ACCEPTED">ACCEPTED</option>
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Min CGPA</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 7.5"
              value={minCgpa}
              onChange={(e) => setMinCgpa(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Graduation Year</label>
            <input
              type="number"
              placeholder="e.g. 2026"
              value={gradYear}
              onChange={(e) => setGradYear(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-xs font-semibold">{error}</p>
        </div>
      )}

      {/* Applications Roster List */}
      {applications.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center max-w-md mx-auto space-y-2">
          <Users className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-900">No candidate applications found</h3>
          <p className="text-xs text-slate-500">No student applications match the selected status or eligibility criteria.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Candidate</th>
                  <th className="px-4 py-3">Institution & Dept</th>
                  <th className="px-4 py-3">Opportunity</th>
                  <th className="px-4 py-3">Academics</th>
                  <th className="px-4 py-3">Applied On</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/50 transition">
                    <td className="px-4 py-3">
                      <p className="font-bold text-slate-900">{app.student.first_name} {app.student.last_name}</p>
                      <p className="text-[10px] text-slate-400">Roll: {app.student.roll_number}</p>
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-semibold text-slate-800">{app.student.institution_name}</p>
                      <p className="text-[10px] text-slate-500">{app.student.department_name}</p>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-700">{app.opportunity_title}</td>
                    <td className="px-4 py-3">
                      <p className="font-bold text-emerald-700">CGPA: {app.student.cgpa || 'N/A'}</p>
                      <p className="text-[10px] text-slate-500">Class of {app.student.graduation_year}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold ${
                        app.current_status === 'APPLIED' ? 'bg-blue-100 text-blue-800' :
                        app.current_status === 'SHORTLISTED' ? 'bg-amber-100 text-amber-800' :
                        app.current_status === 'INTERVIEWING' ? 'bg-purple-100 text-purple-800' :
                        app.current_status === 'OFFERED' || app.current_status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {app.current_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => openDetailModal(app)}
                        className="px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg font-bold text-[11px] transition"
                      >
                        Review ATS &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Candidate ATS Detail & Status Update Modal */}
      {selectedApp && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-xl space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div>
                <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wide">ATS Candidate Review</span>
                <h3 className="text-base font-bold text-slate-900">
                  {selectedApp.student.first_name} {selectedApp.student.last_name}
                </h3>
              </div>
              <button onClick={() => setSelectedApp(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Candidate Details */}
            <div className="bg-slate-50 p-4 rounded-xl space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div><span className="font-semibold text-slate-500">Institution:</span> {selectedApp.student.institution_name}</div>
                <div><span className="font-semibold text-slate-500">Department:</span> {selectedApp.student.department_name}</div>
                <div><span className="font-semibold text-slate-500">Roll Number:</span> {selectedApp.student.roll_number}</div>
                <div><span className="font-semibold text-slate-500">CGPA:</span> <span className="font-bold text-emerald-700">{selectedApp.student.cgpa || 'N/A'}</span></div>
                <div><span className="font-semibold text-slate-500">Graduation Year:</span> {selectedApp.student.graduation_year}</div>
                <div><span className="font-semibold text-slate-500">Target Role:</span> {selectedApp.student.target_career_role || 'Software Engineer'}</div>
              </div>
              {selectedApp.student.skills.length > 0 && (
                <div className="pt-2">
                  <span className="font-semibold text-slate-500 block mb-1">Student Skills:</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedApp.student.skills.map((sk, idx) => (
                      <span key={idx} className="px-2 py-0.5 bg-white border border-slate-200 rounded-md text-[10px] text-slate-700 font-medium">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {selectedApp.cover_letter && (
                <div className="pt-2 border-t border-slate-200">
                  <span className="font-semibold text-slate-500 block mb-1">Cover Letter / Note:</span>
                  <p className="text-slate-700 italic bg-white p-2.5 rounded-lg border border-slate-200">{selectedApp.cover_letter}</p>
                </div>
              )}
            </div>

            {/* Update ATS Status Stage */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-900">Update Application Stage</h4>
              <div>
                <label className="block text-[11px] font-semibold text-slate-600 mb-1">Stage Note / Decision Rationale</label>
                <input
                  type="text"
                  placeholder="e.g. Cleared technical interview round 1 with top score."
                  value={notesInput}
                  onChange={(e) => setNotesInput(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                <Button
                  variant={selectedApp.current_status === 'SHORTLISTED' ? 'primary' : 'outline'}
                  size="sm"
                  disabled={updating}
                  onClick={() => handleUpdateStatus('SHORTLISTED')}
                >
                  Shortlist
                </Button>
                <Button
                  variant={selectedApp.current_status === 'INTERVIEWING' ? 'primary' : 'outline'}
                  size="sm"
                  disabled={updating}
                  onClick={() => handleUpdateStatus('INTERVIEWING')}
                >
                  Interviewing
                </Button>
                <Button
                  variant={selectedApp.current_status === 'OFFERED' ? 'primary' : 'outline'}
                  size="sm"
                  disabled={updating}
                  onClick={() => handleUpdateStatus('OFFERED')}
                >
                  Extend Offer
                </Button>
                <Button
                  variant={selectedApp.current_status === 'REJECTED' ? 'primary' : 'outline'}
                  size="sm"
                  disabled={updating}
                  onClick={() => handleUpdateStatus('REJECTED')}
                >
                  Reject
                </Button>
              </div>
            </div>

            {/* Application Status History Timeline */}
            <div className="space-y-2 pt-3 border-t border-slate-200">
              <h4 className="text-xs font-bold text-slate-900">Audit Status History Log</h4>
              {statusHistory.length === 0 ? (
                <p className="text-[11px] text-slate-500">No status changes recorded yet.</p>
              ) : (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {statusHistory.map((h) => (
                    <div key={h.id} className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-[11px] flex justify-between items-center">
                      <div>
                        <span className="font-bold text-blue-700">{h.status}</span>
                        <span className="text-slate-500 ml-2">— {h.notes || 'Status changed'}</span>
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {h.changed_by_name} • {new Date(h.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
