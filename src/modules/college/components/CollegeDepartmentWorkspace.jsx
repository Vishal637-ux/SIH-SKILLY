import React, { useState, useEffect } from 'react';
import { Layers, Users, UserCheck, RefreshCw, AlertTriangle, Building2 } from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function CollegeDepartmentWorkspace() {
  const [departments, setDepartments] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [activeTab, setActiveTab] = useState('departments');

  const fetchData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const [deptRes, facRes] = await Promise.all([
        api.get('/college/departments'),
        api.get('/college/faculty'),
      ]);
      setDepartments(deptRes.data);
      setFaculty(facRes.data);
    } catch (err) {
      console.error('Failed to load department data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load department & faculty roster.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <Loading message="Loading departments & faculty directory..." />;
  }

  if (errorMsg) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
        <h3 className="text-lg font-bold text-red-900">Access Error</h3>
        <p className="text-sm text-red-700">{errorMsg}</p>
        <Button onClick={fetchData} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-1.5" />
          <span>Retry</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('departments')}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'departments'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Layers className="w-4 h-4 inline mr-2" />
            Departments ({departments.length})
          </button>
          <button
            onClick={() => setActiveTab('faculty')}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              activeTab === 'faculty'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <UserCheck className="w-4 h-4 inline mr-2" />
            Faculty & Staff ({faculty.length})
          </button>
        </div>
        <Button onClick={fetchData} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-1.5" />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Departments View */}
      {activeTab === 'departments' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {departments.map((dept) => (
            <div key={dept.id} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm">
                  {dept.code}
                </div>
                <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-medium">Active</span>
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">{dept.name}</h3>
                <p className="text-xs text-slate-500 mt-1">Code: {dept.code}</p>
              </div>
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
                <span>
                  <Users className="w-3.5 h-3.5 inline mr-1 text-slate-400" />
                  {dept.student_count} Students
                </span>
                <span>
                  <UserCheck className="w-3.5 h-3.5 inline mr-1 text-slate-400" />
                  {dept.faculty_count} Faculty
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Faculty View */}
      {activeTab === 'faculty' && (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="py-3.5 px-4 sm:px-6">Faculty / Staff Name</th>
                  <th className="py-3.5 px-4 sm:px-6">Designation</th>
                  <th className="py-3.5 px-4 sm:px-6">Department / Scope</th>
                  <th className="py-3.5 px-4 sm:px-6">Role Type</th>
                  <th className="py-3.5 px-4 sm:px-6">Email</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {faculty.map((member) => (
                  <tr key={member.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-4 sm:px-6 font-semibold text-slate-900">
                      {member.first_name} {member.last_name}
                    </td>
                    <td className="py-4 px-4 sm:px-6 text-slate-600">{member.designation}</td>
                    <td className="py-4 px-4 sm:px-6 text-slate-600">{member.department_name}</td>
                    <td className="py-4 px-4 sm:px-6">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        member.role_type === 'STAFF' ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}>
                        {member.staff_role || member.role_type}
                      </span>
                    </td>
                    <td className="py-4 px-4 sm:px-6 text-slate-500">{member.email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
