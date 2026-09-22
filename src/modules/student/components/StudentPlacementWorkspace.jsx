import React, { useState, useEffect, useMemo } from 'react';
import { 
  Building2, 
  Award, 
  Briefcase, 
  Calendar, 
  DollarSign, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Search, 
  Filter, 
  Sparkles, 
  X, 
  ExternalLink, 
  FileText, 
  Users, 
  GraduationCap, 
  ArrowRight, 
  RefreshCw, 
  Check, 
  Send 
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return String(dateStr);
  }
};

export default function StudentPlacementWorkspace() {
  const [activeTab, setActiveTab] = useState('drives'); // 'drives' | 'records'
  const [opportunities, setOpportunities] = useState([]);
  const [placementRecords, setPlacementRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Search & Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [eligibilityFilter, setEligibilityFilter] = useState('ALL'); // ALL, ELIGIBLE_ONLY

  // Modals
  const [selectedDrive, setSelectedDrive] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [coverLetter, setCoverLetter] = useState('');
  const [applyingDriveId, setApplyingDriveId] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      const [oppsRes, placementsRes] = await Promise.all([
        api.get('/student/opportunities'),
        api.get('/student/placements'),
      ]);

      setOpportunities(oppsRes.data || []);
      setPlacementRecords(placementsRes.data || []);
    } catch (err) {
      console.error('Failed to load student placement data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load placement drives & records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Filtered placement drives (opportunities)
  const filteredDrives = useMemo(() => {
    return opportunities.filter((drive) => {
      const text = `${drive.title} ${drive.company_name} ${drive.description} ${drive.location}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());

      const matchesEligibility =
        eligibilityFilter === 'ALL' || (eligibilityFilter === 'ELIGIBLE_ONLY' && drive.is_eligible);

      return matchesSearch && matchesEligibility;
    });
  }, [opportunities, searchTerm, eligibilityFilter]);

  // Submit drive application
  const handleApplySubmit = async (e) => {
    e?.preventDefault();
    if (!selectedDrive) return;

    try {
      setApplyingDriveId(selectedDrive.id);
      setErrorMsg(null);

      await api.post(`/student/opportunities/${selectedDrive.id}/apply`, {
        cover_letter: coverLetter.trim() || null,
        resume_version_id: null
      });

      setSuccessToast(`Successfully registered/applied for campus drive "${selectedDrive.title}"!`);
      setTimeout(() => setSuccessToast(null), 4000);

      setApplyModalOpen(false);
      setDetailModalOpen(false);
      setCoverLetter('');
      setSelectedDrive(null);

      await fetchData();
    } catch (err) {
      console.error('Failed to register for drive:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to submit drive registration.');
    } finally {
      setApplyingDriveId(null);
    }
  };

  const openApplyModal = (drive) => {
    setSelectedDrive(drive);
    setCoverLetter('');
    setApplyModalOpen(true);
  };

  const openDetailModal = (drive) => {
    setSelectedDrive(drive);
    setDetailModalOpen(true);
  };

  if (loading) {
    return <Loading label="Loading campus placement drives & records..." />;
  }

  return (
    <div className="space-y-6">
      {/* Toast Notifications */}
      {successToast && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-sm flex items-center justify-between shadow-sm animate-fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span className="font-medium">{successToast}</span>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <button 
            onClick={() => setErrorMsg(null)}
            className="text-rose-500 hover:text-rose-700 text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Header & Navigation */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-100 flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-blue-600" />
                Module 09 — Placement & Accreditation Management
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mt-2">
              {activeTab === 'drives' ? 'Campus Placement Drives' : 'My Placement Records'}
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Explore TPO-approved campus recruitment drives, verify CGPA & skill eligibility thresholds, and track confirmed placement records.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl self-start md:self-auto">
            <button
              onClick={() => setActiveTab('drives')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                activeTab === 'drives'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>Campus Drives</span>
              <span className="ml-1 px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded-full font-bold">
                {opportunities.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('records')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                activeTab === 'records'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Award className="w-4 h-4" />
              <span>Confirmed Placements</span>
              <span className="ml-1 px-2 py-0.5 text-xs bg-slate-200 text-slate-700 rounded-full font-bold">
                {placementRecords.length}
              </span>
            </button>
          </div>
        </div>

        {/* Filters bar for Placement Drives */}
        {activeTab === 'drives' && (
          <div className="mt-6 pt-6 border-t border-slate-100 flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search campus drives by company, role title, or location..."
                className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>

            <div className="flex items-center space-x-3 w-full md:w-auto">
              <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <Filter className="w-3.5 h-3.5 text-slate-500" />
                <select
                  value={eligibilityFilter}
                  onChange={(e) => setEligibilityFilter(e.target.value)}
                  className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
                >
                  <option value="ALL">All Drives</option>
                  <option value="ELIGIBLE_ONLY">Eligible Drives Only</option>
                </select>
              </div>

              <button
                onClick={fetchData}
                title="Refresh Placement Drives"
                className="p-2 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: CAMPUS PLACEMENT DRIVES */}
      {/* ========================================================================= */}
      {activeTab === 'drives' && (
        <>
          {filteredDrives.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-4 shadow-sm">
              <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto">
                <Building2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800">No campus placement drives found</h3>
              <p className="text-slate-500 text-sm max-w-md mx-auto">
                {searchTerm || eligibilityFilter !== 'ALL'
                  ? 'No placement drives match your filter criteria. Try adjusting filters.'
                  : 'There are currently no active campus placement drives scheduled.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredDrives.map((drive) => {
                const matchPct = Math.round(drive.skill_match_percentage || 0);
                const minCgpa = drive.eligibility_criteria?.min_cgpa;
                const gradYear = drive.eligibility_criteria?.graduation_year;

                return (
                  <div
                    key={drive.id}
                    className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between hover:border-blue-300 hover:shadow-md transition-all group"
                  >
                    <div className="space-y-4">
                      {/* Company & Title Header */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-11 h-11 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-bold overflow-hidden flex-shrink-0">
                            {drive.company_logo_url ? (
                              <img src={drive.company_logo_url} alt={drive.company_name} className="w-full h-full object-cover" />
                            ) : (
                              <Building2 className="w-5 h-5 text-blue-600" />
                            )}
                          </div>
                          <div>
                            <span className="text-xs font-semibold text-slate-500">{drive.company_name}</span>
                            <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">
                              {drive.title}
                            </h3>
                          </div>
                        </div>

                        <span className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-bold rounded-lg border border-blue-100 flex-shrink-0">
                          {drive.role_type || 'CAMPUS_DRIVE'}
                        </span>
                      </div>

                      {/* Package, Location, Openings */}
                      <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-600 border-y border-slate-100 py-3">
                        {drive.stipend_salary && (
                          <div className="flex items-center space-x-1.5 font-bold text-emerald-700">
                            <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                            <span>{drive.stipend_salary}</span>
                          </div>
                        )}

                        <div className="flex items-center space-x-1.5">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>{drive.location || 'Campus / Remote'}</span>
                          {drive.is_remote && (
                            <span className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-semibold rounded">
                              Remote
                            </span>
                          )}
                        </div>

                        <div className="flex items-center space-x-1.5">
                          <Users className="w-3.5 h-3.5 text-slate-400" />
                          <span>{drive.openings_count} position{drive.openings_count > 1 ? 's' : ''}</span>
                        </div>
                      </div>

                      {/* Eligibility Criteria Cards */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                          <span className="flex items-center gap-1">
                            <GraduationCap className="w-4 h-4 text-blue-600" />
                            Eligibility Criteria
                          </span>
                          <span className="text-slate-400 text-[11px]">
                            Deadline: {formatDate(drive.application_deadline)}
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-2 text-xs">
                          {minCgpa !== undefined && minCgpa !== null && (
                            <div className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium">
                              Min CGPA: <span className="font-bold text-slate-900">{minCgpa}</span>
                            </div>
                          )}

                          {gradYear && (
                            <div className="px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-medium">
                              Batch: <span className="font-bold text-slate-900">{gradYear}</span>
                            </div>
                          )}
                        </div>

                        {/* Status Diagnostics */}
                        <div className="pt-2">
                          {drive.is_eligible ? (
                            <div className="flex items-center space-x-1.5 text-xs text-emerald-700 font-semibold bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl">
                              <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                              <span>Eligible — Skill Match {matchPct}%</span>
                            </div>
                          ) : (
                            <div className="flex items-start space-x-1.5 text-xs text-amber-800 font-medium bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-xl">
                              <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <span className="font-semibold block">Eligibility Warning:</span>
                                {drive.eligibility_reasons && drive.eligibility_reasons.length > 0 ? (
                                  <span className="text-[11px] text-slate-600">{drive.eligibility_reasons[0]}</span>
                                ) : (
                                  <span className="text-[11px] text-slate-600">Does not meet batch criteria.</span>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Required Skills */}
                      {drive.required_skills && drive.required_skills.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {drive.required_skills.slice(0, 4).map((sk) => (
                            <span
                              key={sk.skill_id}
                              className={`text-[11px] px-2 py-0.5 rounded-md font-medium border ${
                                sk.is_mandatory
                                  ? 'bg-blue-50 text-blue-700 border-blue-100'
                                  : 'bg-slate-50 text-slate-600 border-slate-200'
                              }`}
                            >
                              {sk.skill_name} {sk.is_mandatory && '*'}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                      <button
                        onClick={() => openDetailModal(drive)}
                        className="text-xs font-semibold text-slate-600 hover:text-blue-600 transition-colors flex items-center space-x-1"
                      >
                        <span>View Drive Details</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>

                      {drive.has_applied ? (
                        <button
                          disabled
                          className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                        >
                          <Check className="w-4 h-4 text-emerald-600" />
                          <span>Registered</span>
                        </button>
                      ) : (
                        <Button
                          variant="primary"
                          onClick={() => openApplyModal(drive)}
                          disabled={!drive.is_eligible}
                          title={!drive.is_eligible ? 'You do not meet CGPA or skill eligibility criteria' : 'Register for placement drive'}
                          className="text-xs py-2 px-4 bg-blue-600 hover:bg-blue-700"
                        >
                          <span>Register for Drive</span>
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: CONFIRMED PLACEMENT RECORDS */}
      {/* ========================================================================= */}
      {activeTab === 'records' && (
        <>
          {placementRecords.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-4 shadow-sm">
              <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center mx-auto">
                <Award className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800">No confirmed placement records yet</h3>
              <p className="text-slate-500 text-sm max-w-md mx-auto">
                Your official placement offers logged by your institutional Training & Placement Officer (TPO) will appear here.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {placementRecords.map((rec) => (
                <div key={rec.id} className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 font-bold">
                        <Award className="w-5 h-5" />
                      </div>
                      <div>
                        <span className="text-xs font-semibold text-slate-500">{rec.company_name}</span>
                        <h3 className="text-base font-bold text-slate-900">{rec.opportunity_title || 'Campus Placement Offer'}</h3>
                      </div>
                    </div>
                    <span className="px-3 py-1 bg-emerald-100 text-emerald-800 border border-emerald-200 text-xs font-bold rounded-full">
                      {rec.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                    <div>
                      <span className="text-slate-500 block">Package (LPA)</span>
                      <span className="font-bold text-emerald-700 text-sm">₹{rec.package_lpa} LPA</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Institution</span>
                      <span className="font-semibold text-slate-800">{rec.institution_name}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Offer Date</span>
                      <span className="font-medium text-slate-800">{formatDate(rec.offer_date)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Joining Date</span>
                      <span className="font-medium text-slate-800">{formatDate(rec.joining_date) || 'To be confirmed'}</span>
                    </div>
                  </div>

                  {rec.offer_letter_url && (
                    <div className="pt-2">
                      <a
                        href={rec.offer_letter_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center space-x-1"
                      >
                        <FileText className="w-4 h-4" />
                        <span>View Official Offer Letter</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ========================================================================= */}
      {/* DRIVE DETAIL MODAL */}
      {/* ========================================================================= */}
      {detailModalOpen && selectedDrive && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-100 flex items-start justify-between sticky top-0 bg-white z-10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-bold overflow-hidden">
                  {selectedDrive.company_logo_url ? (
                    <img src={selectedDrive.company_logo_url} alt={selectedDrive.company_name} className="w-full h-full object-cover" />
                  ) : (
                    <Building2 className="w-6 h-6 text-blue-600" />
                  )}
                </div>
                <div>
                  <span className="text-xs font-semibold text-slate-500">{selectedDrive.company_name}</span>
                  <h2 className="text-lg font-bold text-slate-900">{selectedDrive.title}</h2>
                </div>
              </div>

              <button
                onClick={() => setDetailModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <div>
                  <span className="text-slate-500 block">Compensation</span>
                  <span className="font-bold text-emerald-700">{selectedDrive.stipend_salary || 'As per norms'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Location</span>
                  <span className="font-bold text-slate-800">{selectedDrive.location}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Min CGPA</span>
                  <span className="font-bold text-slate-800">{selectedDrive.eligibility_criteria?.min_cgpa ?? 'None'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Batch</span>
                  <span className="font-bold text-slate-800">{selectedDrive.eligibility_criteria?.graduation_year ?? 'All'}</span>
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="text-sm font-bold text-slate-900">Job & Drive Description</h3>
                <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line">
                  {selectedDrive.description}
                </p>
              </div>

              {selectedDrive.required_skills && selectedDrive.required_skills.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900">Required Skills & Proficiency</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedDrive.required_skills.map((sk) => (
                      <div key={sk.skill_id} className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-xs flex items-center justify-between">
                        <div>
                          <span className="font-semibold text-slate-800">{sk.skill_name}</span>
                          <span className="text-[11px] text-slate-500 block">Level: {sk.required_proficiency}</span>
                        </div>
                        {sk.is_mandatory && (
                          <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-[10px] font-bold rounded">
                            Mandatory
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-slate-100 flex items-center justify-end space-x-3 bg-white sticky bottom-0">
              <Button variant="outline" onClick={() => setDetailModalOpen(false)}>
                Close
              </Button>
              {selectedDrive.has_applied ? (
                <button
                  disabled
                  className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                >
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Registered</span>
                </button>
              ) : (
                <Button
                  variant="primary"
                  onClick={() => {
                    setDetailModalOpen(false);
                    openApplyModal(selectedDrive);
                  }}
                  disabled={!selectedDrive.is_eligible}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <span>Register for Drive</span>
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* APPLY / REGISTER MODAL */}
      {/* ========================================================================= */}
      {applyModalOpen && selectedDrive && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-lg">
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold text-blue-600">Campus Placement Registration</span>
                <h2 className="text-lg font-bold text-slate-900 mt-0.5">{selectedDrive.title}</h2>
                <p className="text-xs text-slate-500">{selectedDrive.company_name}</p>
              </div>

              <button
                onClick={() => setApplyModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleApplySubmit} className="p-6 space-y-4">
              <div className="p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-800 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span>Your verified CGPA, department enrollment, and skill passport will be transmitted to the company TPO portal.</span>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700">
                  Notes / Statement of Purpose <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <textarea
                  rows={4}
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  placeholder="Include any specific details for the recruiter or TPO..."
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setApplyModalOpen(false)}
                  disabled={applyingDriveId === selectedDrive.id}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={applyingDriveId === selectedDrive.id}
                  className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{applyingDriveId === selectedDrive.id ? 'Submitting...' : 'Confirm Drive Registration'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
