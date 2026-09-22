import React, { useState, useEffect } from 'react';
import { 
  Briefcase, Search, Filter, CheckCircle2, Award, 
  Building2, Calendar, DollarSign, Users, AlertCircle, RefreshCw, X, ChevronRight
} from 'lucide-react';
import api from '../../../lib/api';

export default function CollegePlacementDriveWorkspace() {
  const [drives, setDrives] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Shortlisting Modal state
  const [selectedDrive, setSelectedDrive] = useState(null);
  const [shortlistParams, setShortlistParams] = useState({
    min_cgpa: 7.0,
    graduation_year: 2025,
    department_ids: [],
    min_proficiency: 'INTERMEDIATE'
  });
  const [shortlistResults, setShortlistResults] = useState(null);
  const [shortlistingLoading, setShortlistingLoading] = useState(false);
  const [shortlistError, setShortlistError] = useState(null);

  // Placement Modal state
  const [placementStudent, setPlacementStudent] = useState(null);
  const [placementData, setPlacementData] = useState({
    company_name: '',
    designation: '',
    package_amount: 8.0,
    placement_type: 'ON_CAMPUS'
  });
  const [placementLoading, setPlacementLoading] = useState(false);
  const [placementSuccess, setPlacementSuccess] = useState(null);
  const [placementError, setPlacementError] = useState(null);

  useEffect(() => {
    fetchDrives();
    fetchDepartments();
  }, []);

  const fetchDrives = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/college/drives');
      setDrives(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch campus drives');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const res = await api.get('/college/departments');
      setDepartments(res.data || []);
    } catch (err) {
      console.error("Failed to fetch departments", err);
    }
  };

  const handleOpenShortlisting = (drive) => {
    setSelectedDrive(drive);
    setShortlistResults(null);
    setShortlistError(null);
    setShortlistParams({
      min_cgpa: drive.min_cgpa || 7.0,
      graduation_year: 2025,
      department_ids: [],
      min_proficiency: 'INTERMEDIATE'
    });
  };

  const handleRunShortlisting = async () => {
    if (!selectedDrive) return;
    setShortlistingLoading(true);
    setShortlistError(null);
    try {
      const payload = {
        opportunity_id: selectedDrive.id,
        min_cgpa: parseFloat(shortlistParams.min_cgpa),
        graduation_year: shortlistParams.graduation_year ? parseInt(shortlistParams.graduation_year) : null,
        department_ids: shortlistParams.department_ids,
        min_proficiency: shortlistParams.min_proficiency
      };
      const res = await api.post('/college/shortlist', payload);
      setShortlistResults(res.data);
    } catch (err) {
      setShortlistError(err.response?.data?.detail || 'Shortlisting evaluation failed');
    } finally {
      setShortlistingLoading(false);
    }
  };

  const handleOpenPlacementRecord = (student) => {
    setPlacementStudent(student);
    setPlacementData({
      company_name: selectedDrive?.company_name || '',
      designation: selectedDrive?.title || 'Software Engineer',
      package_amount: selectedDrive?.package_lpa || 8.0,
      placement_type: 'ON_CAMPUS'
    });
    setPlacementError(null);
    setPlacementSuccess(null);
  };

  const handleRecordPlacement = async (e) => {
    e.preventDefault();
    if (!placementStudent) return;
    setPlacementLoading(true);
    setPlacementError(null);
    try {
      const payload = {
        student_id: placementStudent.student_id,
        opportunity_id: selectedDrive?.id,
        company_name: placementData.company_name,
        designation: placementData.designation,
        package_amount: parseFloat(placementData.package_amount),
        placement_type: placementData.placement_type
      };
      const res = await api.post('/college/placements', payload);
      setPlacementSuccess(`Placement confirmed for ${placementStudent.full_name}!`);
      setTimeout(() => {
        setPlacementStudent(null);
        setPlacementSuccess(null);
      }, 2000);
    } catch (err) {
      setPlacementError(err.response?.data?.detail || 'Failed to record placement');
    } finally {
      setPlacementLoading(false);
    }
  };

  const toggleDepartmentSelection = (depId) => {
    setShortlistParams(prev => {
      const exists = prev.department_ids.includes(depId);
      return {
        ...prev,
        department_ids: exists 
          ? prev.department_ids.filter(id => id !== depId)
          : [...prev.department_ids, depId]
      };
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-indigo-600" />
            Campus Placement Drives
          </h2>
          <p className="text-sm text-slate-500">
            Consume active company opportunities, execute deterministic student eligibility filtering, and log confirmed placements.
          </p>
        </div>
        <button 
          onClick={fetchDrives}
          className="flex items-center gap-2 px-3.5 py-2 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Drives
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Drives Grid */}
      {loading ? (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-100 shadow-sm">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-slate-500 text-sm">Loading active placement opportunities...</p>
        </div>
      ) : drives.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-100 shadow-sm space-y-3">
          <Building2 className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-slate-700 font-medium">No Active Drives Available</h3>
          <p className="text-slate-400 text-sm">Opportunities published by Industry partners will appear here for campus consumption.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {drives.map(drive => (
            <div key={drive.id} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 hover:border-indigo-200 transition space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">
                    {drive.opportunity_type || 'JOB'}
                  </span>
                  <h3 className="text-lg font-bold text-slate-800 mt-2">{drive.title}</h3>
                  <div className="text-sm font-medium text-slate-600 flex items-center gap-1.5 mt-0.5">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    {drive.company_name}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-lg font-extrabold text-emerald-600">
                    {drive.package_lpa ? `₹${drive.package_lpa} LPA` : 'Competitive'}
                  </span>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">{drive.status}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 py-3 bg-slate-50 rounded-lg px-3 text-xs text-slate-600">
                <div>Location: <span className="font-semibold text-slate-800">{drive.location || 'Remote/Hybrid'}</span></div>
                <div>Min CGPA: <span className="font-semibold text-slate-800">{drive.min_cgpa || 'None'}</span></div>
                <div>Applications: <span className="font-semibold text-indigo-600">{drive.applicant_count || 0} enrolled</span></div>
                <div>Deadline: <span className="font-semibold text-slate-800">{drive.deadline ? new Date(drive.deadline).toLocaleDateString() : 'Open'}</span></div>
              </div>

              {/* Skills required */}
              {drive.required_skills && drive.required_skills.length > 0 && (
                <div className="space-y-1.5">
                  <div className="text-xs font-semibold text-slate-500">Required Skills:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {drive.required_skills.map((s, i) => (
                      <span key={i} className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                        {s.name} ({s.min_proficiency})
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-2 flex gap-3">
                <button
                  onClick={() => handleOpenShortlisting(drive)}
                  className="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition flex items-center justify-center gap-2"
                >
                  <Users className="w-4 h-4" />
                  Run Eligibility Shortlist
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Shortlisting Modal & Results Workspace */}
      {selectedDrive && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex justify-between items-start border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-semibold uppercase text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                  Deterministic Criteria Engine
                </span>
                <h2 className="text-xl font-bold text-slate-800 mt-1">
                  Shortlist Candidates for {selectedDrive.title}
                </h2>
                <p className="text-sm text-slate-500">{selectedDrive.company_name}</p>
              </div>
              <button 
                onClick={() => setSelectedDrive(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Criteria Controls */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Configured Filtering Rules</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Min CGPA Threshold</label>
                  <input
                    type="number"
                    step="0.1"
                    value={shortlistParams.min_cgpa}
                    onChange={(e) => setShortlistParams({ ...shortlistParams, min_cgpa: e.target.value })}
                    className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Target Graduation Year</label>
                  <input
                    type="number"
                    value={shortlistParams.graduation_year}
                    onChange={(e) => setShortlistParams({ ...shortlistParams, graduation_year: e.target.value })}
                    className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Min Skill Proficiency</label>
                  <select
                    value={shortlistParams.min_proficiency}
                    onChange={(e) => setShortlistParams({ ...shortlistParams, min_proficiency: e.target.value })}
                    className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
                  >
                    <option value="BEGINNER">BEGINNER</option>
                    <option value="INTERMEDIATE">INTERMEDIATE</option>
                    <option value="ADVANCED">ADVANCED</option>
                    <option value="EXPERT">EXPERT</option>
                  </select>
                </div>
              </div>

              {/* Department Checkboxes */}
              {departments.length > 0 && (
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-600">Restricted Departments (Leave empty for all):</label>
                  <div className="flex flex-wrap gap-2">
                    {departments.map(dep => {
                      const selected = shortlistParams.department_ids.includes(dep.id);
                      return (
                        <button
                          key={dep.id}
                          type="button"
                          onClick={() => toggleDepartmentSelection(dep.id)}
                          className={`text-xs px-2.5 py-1 rounded-md font-medium border transition ${
                            selected 
                              ? 'bg-indigo-600 text-white border-indigo-600' 
                              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                          }`}
                        >
                          {dep.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <button
                onClick={handleRunShortlisting}
                disabled={shortlistingLoading}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
              >
                {shortlistingLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Evaluating PostgreSQL Student Criteria...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    Evaluate & Fetch Eligible Candidates
                  </>
                )}
              </button>
            </div>

            {shortlistError && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-lg text-xs font-medium">
                {shortlistError}
              </div>
            )}

            {/* Results Section */}
            {shortlistResults && (
              <div className="space-y-4 pt-2">
                <div className="flex justify-between items-center bg-indigo-50 border border-indigo-100 p-4 rounded-xl">
                  <div>
                    <h3 className="font-bold text-indigo-900">Deterministic Match Output</h3>
                    <p className="text-xs text-indigo-700">
                      Evaluated {shortlistResults.total_evaluated_students} institutional candidates.
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-black text-indigo-600">
                      {shortlistResults.eligible_count}
                    </span>
                    <span className="text-xs text-indigo-600 font-medium block">Eligible Candidates</span>
                  </div>
                </div>

                <div className="max-h-60 overflow-y-auto border border-slate-200 rounded-xl divide-y divide-slate-100">
                  {shortlistResults.eligible_students.length === 0 ? (
                    <div className="p-6 text-center text-slate-500 text-sm">
                      No students meet all specified eligibility criteria.
                    </div>
                  ) : (
                    shortlistResults.eligible_students.map(student => (
                      <div key={student.student_id} className="p-3.5 flex justify-between items-center hover:bg-slate-50 transition">
                        <div>
                          <div className="font-semibold text-slate-800">{student.full_name}</div>
                          <div className="text-xs text-slate-500">
                            {student.department_name} • CGPA: <span className="font-bold text-slate-700">{student.cgpa}</span> • Batch {student.graduation_year}
                          </div>
                          <div className="text-xs text-emerald-600 font-medium mt-0.5">
                            Matching Skills: {student.matching_skills_count} verified
                          </div>
                        </div>
                        <button
                          onClick={() => handleOpenPlacementRecord(student)}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                        >
                          <Award className="w-3.5 h-3.5" />
                          Log Placement
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmed Placement Form Modal */}
      {placementStudent && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <Award className="w-5 h-5 text-emerald-600" />
                Record Confirmed Placement
              </h3>
              <button onClick={() => setPlacementStudent(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-emerald-50 border border-emerald-100 p-3 rounded-lg text-xs text-emerald-800">
              Candidate: <span className="font-bold">{placementStudent.full_name}</span> ({placementStudent.department_name})
            </div>

            {placementSuccess && (
              <div className="p-3 bg-emerald-100 text-emerald-800 rounded-lg text-xs font-semibold">
                {placementSuccess}
              </div>
            )}

            {placementError && (
              <div className="p-3 bg-rose-50 text-rose-700 rounded-lg text-xs font-semibold">
                {placementError}
              </div>
            )}

            <form onSubmit={handleRecordPlacement} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={placementData.company_name}
                  onChange={(e) => setPlacementData({ ...placementData, company_name: e.target.value })}
                  className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Designation</label>
                <input
                  type="text"
                  required
                  value={placementData.designation}
                  onChange={(e) => setPlacementData({ ...placementData, designation: e.target.value })}
                  className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Package Offered (LPA)</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={placementData.package_amount}
                  onChange={(e) => setPlacementData({ ...placementData, package_amount: e.target.value })}
                  className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Placement Channel</label>
                <select
                  value={placementData.placement_type}
                  onChange={(e) => setPlacementData({ ...placementData, placement_type: e.target.value })}
                  className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2"
                >
                  <option value="ON_CAMPUS">ON_CAMPUS</option>
                  <option value="OFF_CAMPUS">OFF_CAMPUS</option>
                  <option value="PPO">PPO (Pre-Placement Offer)</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setPlacementStudent(null)}
                  className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={placementLoading}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm transition disabled:opacity-50"
                >
                  {placementLoading ? 'Recording...' : 'Confirm & Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
