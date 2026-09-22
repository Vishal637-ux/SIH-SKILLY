import React, { useState, useEffect, useMemo } from 'react';
import { 
  Briefcase, 
  Building2, 
  MapPin, 
  DollarSign, 
  Clock, 
  Users, 
  CheckCircle2, 
  AlertCircle, 
  Search, 
  Filter, 
  Sparkles, 
  FileText, 
  X, 
  Calendar, 
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Send,
  RefreshCw,
  Check
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

const STATUS_COLORS = {
  APPLIED: 'bg-blue-100 text-blue-800 border-blue-200',
  SHORTLISTED: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  INTERVIEW_SCHEDULED: 'bg-purple-100 text-purple-800 border-purple-200',
  TECHNICAL_ROUND: 'bg-indigo-100 text-indigo-800 border-indigo-200',
  OFFERED: 'bg-teal-100 text-teal-800 border-teal-200',
  ACCEPTED: 'bg-green-100 text-green-800 border-green-200',
  REJECTED: 'bg-rose-100 text-rose-800 border-rose-200',
  WITHDRAWN: 'bg-gray-100 text-gray-800 border-gray-200'
};

export default function StudentInternshipsWorkspace({ initialTab = 'opportunities' }) {
  const [activeTab, setActiveTab] = useState(initialTab); // 'opportunities' | 'applications'
  const [opportunities, setOpportunities] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Filters & Search for Opportunities
  const [searchTerm, setSearchTerm] = useState('');
  const [roleTypeFilter, setRoleTypeFilter] = useState('ALL');
  const [workModeFilter, setWorkModeFilter] = useState('ALL');

  // Modals
  const [selectedOpp, setSelectedOpp] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [coverLetter, setCoverLetter] = useState('');
  const [applyingOppId, setApplyingOppId] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      const [oppsRes, appsRes] = await Promise.all([
        api.get('/student/opportunities'),
        api.get('/student/applications'),
      ]);

      setOpportunities(oppsRes.data || []);
      setApplications(appsRes.data || []);
    } catch (err) {
      console.error('Failed to load student opportunity data:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load opportunity and application data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Derived filtered opportunities
  const filteredOpportunities = useMemo(() => {
    return opportunities.filter((opp) => {
      // Search text match
      const text = `${opp.title} ${opp.company_name} ${opp.description} ${opp.location}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());

      // Role type match
      const matchesRole = roleTypeFilter === 'ALL' || opp.role_type === roleTypeFilter;

      // Work mode match
      let matchesMode = true;
      if (workModeFilter === 'REMOTE') matchesMode = opp.is_remote === true;
      if (workModeFilter === 'ONSITE') matchesMode = opp.is_remote === false;

      return matchesSearch && matchesRole && matchesMode;
    });
  }, [opportunities, searchTerm, roleTypeFilter, workModeFilter]);

  // Handle Application submission
  const handleApplySubmit = async (e) => {
    e?.preventDefault();
    if (!selectedOpp) return;

    try {
      setApplyingOppId(selectedOpp.id);
      setErrorMsg(null);

      await api.post(`/student/opportunities/${selectedOpp.id}/apply`, {
        cover_letter: coverLetter.trim() || null,
        resume_version_id: null
      });

      setSuccessToast(`Application for "${selectedOpp.title}" submitted successfully!`);
      setTimeout(() => setSuccessToast(null), 4000);

      setApplyModalOpen(false);
      setDetailModalOpen(false);
      setCoverLetter('');
      setSelectedOpp(null);

      // Refresh data
      await fetchData();
    } catch (err) {
      console.error('Failed to submit application:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to submit application. Please try again.');
    } finally {
      setApplyingOppId(null);
    }
  };

  const openApplyModal = (opp) => {
    setSelectedOpp(opp);
    setCoverLetter('');
    setApplyModalOpen(true);
  };

  const openDetailModal = (opp) => {
    setSelectedOpp(opp);
    setDetailModalOpen(true);
  };

  if (loading) {
    return <Loading label="Loading internship & project opportunities..." />;
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

      {/* Header & Navigation Tabs */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full border border-indigo-100 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                Module 09 — Opportunity & Internship ATS
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mt-2">
              {activeTab === 'opportunities' ? 'Internship & Project Opportunities' : 'My Applications'}
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Discover skill-matched corporate internships, review eligibility diagnostics, and track application status.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl self-start md:self-auto">
            <button
              onClick={() => setActiveTab('opportunities')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                activeTab === 'opportunities'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Briefcase className="w-4 h-4" />
              <span>Opportunities</span>
              <span className="ml-1 px-2 py-0.5 text-xs bg-indigo-50 text-indigo-700 rounded-full font-bold">
                {opportunities.length}
              </span>
            </button>
            <button
              onClick={() => setActiveTab('applications')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center space-x-2 ${
                activeTab === 'applications'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>My Applications</span>
              <span className="ml-1 px-2 py-0.5 text-xs bg-slate-200 text-slate-700 rounded-full font-bold">
                {applications.length}
              </span>
            </button>
          </div>
        </div>

        {/* Tab 1: Opportunities Filters & Controls */}
        {activeTab === 'opportunities' && (
          <div className="mt-6 pt-6 border-t border-slate-100 flex flex-col md:flex-row gap-4 items-center justify-between">
            {/* Search input */}
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by title, company, skills, or location..."
                className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
            </div>

            {/* Filter Dropdowns */}
            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
              <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <Filter className="w-3.5 h-3.5 text-slate-500" />
                <select
                  value={roleTypeFilter}
                  onChange={(e) => setRoleTypeFilter(e.target.value)}
                  className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
                >
                  <option value="ALL">All Role Types</option>
                  <option value="INTERNSHIP">Internship</option>
                  <option value="FULL_TIME">Full Time</option>
                  <option value="PROJECT">Project</option>
                </select>
              </div>

              <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <select
                  value={workModeFilter}
                  onChange={(e) => setWorkModeFilter(e.target.value)}
                  className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none cursor-pointer"
                >
                  <option value="ALL">All Modes</option>
                  <option value="REMOTE">Remote Only</option>
                  <option value="ONSITE">Onsite / Hybrid</option>
                </select>
              </div>

              <button
                onClick={fetchData}
                title="Refresh Opportunities"
                className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: BROWSE OPPORTUNITIES LIST */}
      {/* ========================================================================= */}
      {activeTab === 'opportunities' && (
        <>
          {filteredOpportunities.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-4 shadow-sm">
              <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto">
                <Briefcase className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800">No opportunities found</h3>
              <p className="text-slate-500 text-sm max-w-md mx-auto">
                {searchTerm || roleTypeFilter !== 'ALL' || workModeFilter !== 'ALL'
                  ? 'No opportunities match your current filter settings. Try clearing filters.'
                  : 'There are currently no open internship or project opportunities.'}
              </p>
              {(searchTerm || roleTypeFilter !== 'ALL' || workModeFilter !== 'ALL') && (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setRoleTypeFilter('ALL');
                    setWorkModeFilter('ALL');
                  }}
                  className="px-4 py-2 bg-slate-100 text-slate-700 text-sm font-semibold rounded-xl hover:bg-slate-200 transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredOpportunities.map((opp) => {
                const matchPct = Math.round(opp.skill_match_percentage || 0);

                return (
                  <div
                    key={opp.id}
                    className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between hover:border-indigo-200 hover:shadow-md transition-all group"
                  >
                    <div className="space-y-4">
                      {/* Top Bar: Company & Badges */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-bold overflow-hidden flex-shrink-0">
                            {opp.company_logo_url ? (
                              <img src={opp.company_logo_url} alt={opp.company_name} className="w-full h-full object-cover" />
                            ) : (
                              <Building2 className="w-5 h-5 text-indigo-600" />
                            )}
                          </div>
                          <div>
                            <span className="text-xs font-medium text-slate-500">{opp.company_name}</span>
                            <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-1">
                              {opp.title}
                            </h3>
                          </div>
                        </div>

                        {/* Role Type Badge */}
                        <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 flex-shrink-0">
                          {opp.role_type || 'INTERNSHIP'}
                        </span>
                      </div>

                      {/* Details row: Location, Mode, Stipend, Duration */}
                      <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-600 border-y border-slate-100 py-3">
                        <div className="flex items-center space-x-1.5">
                          <MapPin className="w-3.5 h-3.5 text-slate-400" />
                          <span>{opp.location || 'Flexible'}</span>
                          {opp.is_remote && (
                            <span className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-semibold rounded border border-emerald-100">
                              Remote
                            </span>
                          )}
                        </div>

                        {opp.stipend_salary && (
                          <div className="flex items-center space-x-1.5 font-medium text-emerald-700">
                            <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                            <span>{opp.stipend_salary}</span>
                          </div>
                        )}

                        {opp.duration_months && (
                          <div className="flex items-center space-x-1.5">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            <span>{opp.duration_months} Month{opp.duration_months > 1 ? 's' : ''}</span>
                          </div>
                        )}

                        <div className="flex items-center space-x-1.5">
                          <Users className="w-3.5 h-3.5 text-slate-400" />
                          <span>{opp.openings_count} opening{opp.openings_count > 1 ? 's' : ''}</span>
                        </div>
                      </div>

                      {/* Skill Compatibility & Eligibility Diagnostics */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-500 font-medium flex items-center gap-1">
                            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                            Skill Match Diagnostics
                          </span>
                          <span className="font-bold text-indigo-700">{matchPct}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full transition-all rounded-full ${
                              matchPct >= 80
                                ? 'bg-emerald-500'
                                : matchPct >= 50
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${matchPct}%` }}
                          />
                        </div>

                        {/* Eligibility Status Badge */}
                        <div className="flex items-center justify-between pt-1">
                          {opp.is_eligible ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                              <ShieldCheck className="w-3 h-3 text-emerald-600" />
                              Fully Eligible
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
                              <AlertCircle className="w-3 h-3 text-amber-600" />
                              Eligibility Warnings
                            </span>
                          )}

                          <span className="text-[11px] text-slate-400">
                            Apply by: {formatDate(opp.application_deadline)}
                          </span>
                        </div>
                      </div>

                      {/* Required Skills tags */}
                      {opp.required_skills && opp.required_skills.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {opp.required_skills.slice(0, 4).map((sk) => (
                            <span
                              key={sk.skill_id}
                              className={`text-[11px] px-2 py-0.5 rounded-md font-medium border ${
                                sk.is_mandatory
                                  ? 'bg-indigo-50 text-indigo-700 border-indigo-100'
                                  : 'bg-slate-50 text-slate-600 border-slate-200'
                              }`}
                            >
                              {sk.skill_name} {sk.is_mandatory && '*'}
                            </span>
                          ))}
                          {opp.required_skills.length > 4 && (
                            <span className="text-[11px] px-2 py-0.5 bg-slate-100 text-slate-500 rounded-md font-medium">
                              +{opp.required_skills.length - 4} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                      <button
                        onClick={() => openDetailModal(opp)}
                        className="text-xs font-semibold text-slate-600 hover:text-indigo-600 transition-colors flex items-center space-x-1"
                      >
                        <span>View Details</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>

                      {opp.has_applied ? (
                        <button
                          disabled
                          className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                        >
                          <Check className="w-4 h-4 text-emerald-600" />
                          <span>Applied</span>
                        </button>
                      ) : (
                        <Button
                          variant="primary"
                          onClick={() => openApplyModal(opp)}
                          disabled={!opp.is_eligible}
                          title={!opp.is_eligible ? 'You do not currently meet all eligibility criteria' : 'Apply to this opportunity'}
                          className="text-xs py-2 px-4"
                        >
                          <span>Apply Now</span>
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
      {/* TAB 2: MY APPLICATIONS LIST */}
      {/* ========================================================================= */}
      {activeTab === 'applications' && (
        <>
          {applications.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center space-y-4 shadow-sm">
              <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800">No applications submitted yet</h3>
              <p className="text-slate-500 text-sm max-w-md mx-auto">
                You have not submitted any applications for internships or project opportunities.
              </p>
              <button
                onClick={() => setActiveTab('opportunities')}
                className="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-xl hover:bg-indigo-700 transition-colors"
              >
                Browse Available Opportunities
              </button>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
              <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-800">Submitted Applications ({applications.length})</h3>
                <button
                  onClick={fetchData}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Refresh
                </button>
              </div>

              <div className="divide-y divide-slate-100">
                {applications.map((app) => {
                  const statusClass = STATUS_COLORS[app.current_status] || 'bg-slate-100 text-slate-800 border-slate-200';

                  return (
                    <div key={app.id} className="p-6 hover:bg-slate-50/50 transition-colors">
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Building2 className="w-4 h-4 text-indigo-600" />
                            <span className="text-xs font-semibold text-slate-500">{app.company_name}</span>
                          </div>
                          <h4 className="text-base font-bold text-slate-900">{app.opportunity_title}</h4>
                          <div className="flex items-center space-x-3 text-xs text-slate-500 pt-1">
                            <span className="flex items-center space-x-1">
                              <Calendar className="w-3.5 h-3.5 text-slate-400" />
                              <span>Applied on {formatDate(app.applied_at)}</span>
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 self-start md:self-auto">
                          <span className={`px-3 py-1 text-xs font-bold rounded-full border ${statusClass}`}>
                            {app.current_status.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </div>

                      {app.cover_letter && (
                        <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
                          <span className="font-semibold text-slate-700 block mb-1">Submitted Cover Letter:</span>
                          <p className="line-clamp-2 italic">"{app.cover_letter}"</p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}

      {/* ========================================================================= */}
      {/* MODAL 1: OPPORTUNITY DETAIL MODAL */}
      {/* ========================================================================= */}
      {detailModalOpen && selectedOpp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="p-6 border-b border-slate-100 flex items-start justify-between sticky top-0 bg-white z-10">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 font-bold overflow-hidden flex-shrink-0">
                  {selectedOpp.company_logo_url ? (
                    <img src={selectedOpp.company_logo_url} alt={selectedOpp.company_name} className="w-full h-full object-cover" />
                  ) : (
                    <Building2 className="w-6 h-6 text-indigo-600" />
                  )}
                </div>
                <div>
                  <span className="text-xs font-medium text-slate-500">{selectedOpp.company_name}</span>
                  <h2 className="text-lg font-bold text-slate-900">{selectedOpp.title}</h2>
                </div>
              </div>

              <button
                onClick={() => setDetailModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Quick Info Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                <div>
                  <span className="text-slate-500 block">Role Type</span>
                  <span className="font-bold text-slate-800">{selectedOpp.role_type}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Location</span>
                  <span className="font-bold text-slate-800">{selectedOpp.location} ({selectedOpp.is_remote ? 'Remote' : 'Onsite'})</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Stipend / Salary</span>
                  <span className="font-bold text-emerald-700">{selectedOpp.stipend_salary || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Duration</span>
                  <span className="font-bold text-slate-800">{selectedOpp.duration_months ? `${selectedOpp.duration_months} Months` : 'N/A'}</span>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <h3 className="text-sm font-bold text-slate-900">Description</h3>
                <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-line">
                  {selectedOpp.description}
                </p>
              </div>

              {/* Required Skills */}
              {selectedOpp.required_skills && selectedOpp.required_skills.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900">Required Skills</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedOpp.required_skills.map((sk) => (
                      <div key={sk.skill_id} className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-xs flex items-center justify-between">
                        <div>
                          <span className="font-semibold text-slate-800">{sk.skill_name}</span>
                          <span className="text-[11px] text-slate-500 block">Proficiency: {sk.required_proficiency}</span>
                        </div>
                        {sk.is_mandatory && (
                          <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[10px] font-bold rounded">
                            Mandatory
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Eligibility Diagnostics */}
              <div className="space-y-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-indigo-600" />
                    Eligibility Diagnostics
                  </h3>
                  <span className="text-xs font-bold text-indigo-700">
                    Skill Match: {Math.round(selectedOpp.skill_match_percentage || 0)}%
                  </span>
                </div>

                {selectedOpp.is_eligible ? (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>You satisfy all institutional and skill requirements for this opportunity!</span>
                  </div>
                ) : (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 space-y-1">
                    <div className="flex items-center space-x-2 font-semibold">
                      <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                      <span>Eligibility Criteria Not Met:</span>
                    </div>
                    {selectedOpp.eligibility_reasons && selectedOpp.eligibility_reasons.length > 0 ? (
                      <ul className="list-disc list-inside space-y-0.5 text-slate-700 pl-5">
                        {selectedOpp.eligibility_reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-slate-600 pl-5">General eligibility threshold not satisfied.</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-slate-100 flex items-center justify-end space-x-3 bg-white sticky bottom-0">
              <Button variant="outline" onClick={() => setDetailModalOpen(false)}>
                Close
              </Button>
              {selectedOpp.has_applied ? (
                <button
                  disabled
                  className="px-4 py-2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 cursor-not-allowed"
                >
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Applied</span>
                </button>
              ) : (
                <Button
                  variant="primary"
                  onClick={() => {
                    setDetailModalOpen(false);
                    openApplyModal(selectedOpp);
                  }}
                  disabled={!selectedOpp.is_eligible}
                >
                  <span>Apply to Opportunity</span>
                </Button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: APPLICATION SUBMISSION MODAL */}
      {/* ========================================================================= */}
      {applyModalOpen && selectedOpp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl w-full max-w-lg">
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div>
                <span className="text-xs font-semibold text-indigo-600">Submit Application</span>
                <h2 className="text-lg font-bold text-slate-900 mt-0.5">{selectedOpp.title}</h2>
                <p className="text-xs text-slate-500">{selectedOpp.company_name}</p>
              </div>

              <button
                onClick={() => setApplyModalOpen(false)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleApplySubmit} className="p-6 space-y-4">
              <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl text-xs text-indigo-800 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-indigo-600 flex-shrink-0" />
                <span>Your verified skill profile & academic credentials will be attached automatically.</span>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-slate-700">
                  Cover Letter / Statement of Interest <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <textarea
                  rows={4}
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  placeholder="Explain why you are interested in this opportunity and highlight relevant projects or skills..."
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setApplyModalOpen(false)}
                  disabled={applyingOppId === selectedOpp.id}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={applyingOppId === selectedOpp.id}
                  className="flex items-center space-x-2"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{applyingOppId === selectedOpp.id ? 'Submitting...' : 'Confirm Application'}</span>
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
