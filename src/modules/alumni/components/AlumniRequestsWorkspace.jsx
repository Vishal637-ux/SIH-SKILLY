import React, { useState, useEffect } from 'react';
import api from '../../../lib/api';
import Loading from '../../../components/Loading';
import { Users, CheckCircle2, XCircle, Clock, AlertTriangle, Filter } from 'lucide-react';

export default function AlumniRequestsWorkspace() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [actioningId, setActioningId] = useState(null);

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = statusFilter !== 'ALL' ? `/api/v1/alumni/requests?status=${statusFilter}` : '/api/v1/alumni/requests';
      const res = await api.get(endpoint);
      setRequests(res.data.items || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load mentorship requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [statusFilter]);

  const handleAction = async (connectionId, actionStatus) => {
    setActioningId(connectionId);
    try {
      await api.put(`/api/v1/alumni/requests/${connectionId}`, { status: actionStatus });
      await fetchRequests();
    } catch (err) {
      alert(err.response?.data?.detail || `Failed to update request status to ${actionStatus}`);
    } finally {
      setActioningId(null);
    }
  };

  if (loading) {
    return <Loading label="Loading mentorship requests..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Filter Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Inbound Student Mentorship Requests</h3>
          <p className="text-xs text-slate-500">Review student requests, view academic background, and accept/reject connections.</p>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 bg-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending Only</option>
            <option value="ACCEPTED">Accepted Only</option>
            <option value="REJECTED">Rejected Only</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchRequests} className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-semibold">
            Retry
          </button>
        </div>
      )}

      {requests.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200/80 p-12 text-center shadow-sm space-y-2">
          <Users className="w-10 h-10 text-slate-300 mx-auto" />
          <h4 className="text-sm font-bold text-slate-700">No mentorship requests found</h4>
          <p className="text-xs text-slate-500">There are no mentorship requests matching your selected filter.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((req) => (
            <div key={req.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    {req.student?.first_name} {req.student?.last_name}
                  </h4>
                  <p className="text-xs text-slate-500">
                    {req.student?.institution_name || 'Institution'} • {req.student?.department_name || 'Department'} • Grad Class {req.student?.graduation_year || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                    req.status === 'PENDING' ? 'bg-amber-100 text-amber-800' :
                    req.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                    req.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {req.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-700 block mb-0.5">Target Career Goal:</span>
                  <span className="text-purple-700 font-medium">{req.student?.target_career_role || 'Not specified'}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700 block mb-0.5">Academic Standing & Skills:</span>
                  <span className="text-slate-600">
                    CGPA: {req.student?.cgpa || 'N/A'} | Skills: {req.student?.skills?.length ? req.student.skills.join(', ') : 'None listed'}
                  </span>
                </div>
              </div>

              {req.request_note && (
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-xs text-slate-700">
                  <span className="font-semibold block mb-0.5 text-slate-900">Student Request Message:</span>
                  <p className="italic">{req.request_note}</p>
                </div>
              )}

              {req.status === 'PENDING' && (
                <div className="pt-2 flex justify-end gap-2">
                  <button
                    onClick={() => handleAction(req.id, 'REJECTED')}
                    disabled={actioningId === req.id}
                    className="px-3.5 py-1.5 bg-slate-100 text-slate-700 hover:bg-red-50 hover:text-red-700 border border-slate-300 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Decline Request</span>
                  </button>
                  <button
                    onClick={() => handleAction(req.id, 'ACCEPTED')}
                    disabled={actioningId === req.id}
                    className="px-3.5 py-1.5 bg-purple-700 text-white hover:bg-purple-800 rounded-lg text-xs font-semibold transition shadow-sm flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{actioningId === req.id ? 'Processing...' : 'Accept Mentorship Request'}</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
