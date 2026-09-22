import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  Target, 
  Compass, 
  Search, 
  Filter, 
  CheckCircle2, 
  ArrowRight, 
  ChevronRight, 
  AlertCircle, 
  Sparkles, 
  BookOpen, 
  Briefcase, 
  Check, 
  Clock, 
  TrendingUp, 
  X, 
  Layers, 
  Award, 
  GraduationCap, 
  Building2,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import api from '../../../lib/api';
import useAuth from '../../../hooks/useAuth';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentCareerWorkspace() {
  const { user } = useAuth();

  // State
  const [workspaceData, setWorkspaceData] = useState(null);
  const [careerRoles, setCareerRoles] = useState([]);
  const [selectedRoleDetail, setSelectedRoleDetail] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [savingTarget, setSavingTarget] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('ALL');

  // Fetch initial data
  const loadWorkspace = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      
      const [wsRes, rolesRes] = await Promise.all([
        api.get('/student/career-workspace'),
        api.get('/student/career-roles'),
      ]);

      setWorkspaceData(wsRes.data);
      setCareerRoles(rolesRes.data || []);
    } catch (err) {
      console.error('Failed to load career workspace:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load career workspace data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWorkspace();
  }, []);

  // Compute unique industry domains from live roles
  const availableDomains = useMemo(() => {
    const domains = new Set();
    careerRoles.forEach((r) => {
      if (r.industry_domain) domains.add(r.industry_domain);
    });
    return Array.from(domains).sort();
  }, [careerRoles]);

  // Filtered roles based on search term & domain
  const filteredRoles = useMemo(() => {
    return careerRoles.filter((role) => {
      const matchesDomain = selectedDomain === 'ALL' || role.industry_domain === selectedDomain;
      const term = searchTerm.trim().toLowerCase();
      const matchesSearch =
        !term ||
        role.title.toLowerCase().includes(term) ||
        (role.description && role.description.toLowerCase().includes(term)) ||
        role.industry_domain.toLowerCase().includes(term);
      return matchesDomain && matchesSearch;
    });
  }, [careerRoles, selectedDomain, searchTerm]);

  // View Career Role Details
  const handleOpenRoleDetail = async (roleId) => {
    try {
      setDetailLoading(true);
      setDetailModalOpen(true);
      const res = await api.get(`/student/career-roles/${roleId}`);
      setSelectedRoleDetail(res.data);
    } catch (err) {
      console.error('Failed to load role details:', err);
      setErrorMsg('Failed to load career role details.');
    } finally {
      setDetailLoading(false);
    }
  };

  // Set Target Career Goal
  const handleSelectTargetRole = async (roleId) => {
    try {
      setSavingTarget(true);
      setErrorMsg(null);

      const res = await api.put('/student/target-role', {
        career_role_id: roleId,
      });

      // Update local workspace and roles list state
      const updatedTargetRole = res.data.target_career_role;
      const updatedCompletion = res.data.completion;

      setWorkspaceData((prev) => ({
        ...prev,
        current_target_role: updatedTargetRole,
        completion: updatedCompletion,
      }));

      // Update roles target flag
      setCareerRoles((prev) =>
        prev.map((r) => ({
          ...r,
          is_current_target: r.id === roleId,
        }))
      );

      // If detail modal is open for this role, update it too
      if (selectedRoleDetail && selectedRoleDetail.id === roleId) {
        setSelectedRoleDetail((prev) => ({
          ...prev,
          is_current_target: true,
        }));
      }

      setSuccessToast(res.data.message || 'Target career goal updated successfully!');
      setTimeout(() => setSuccessToast(null), 4000);
    } catch (err) {
      console.error('Failed to set target career goal:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to save target career goal.');
    } finally {
      setSavingTarget(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <Loading message="Loading student career workspace & catalog..." />
      </div>
    );
  }

  const currentTarget = workspaceData?.current_target_role;
  const completion = workspaceData?.completion || {};

  return (
    <div className="space-y-6 sm:space-y-8 animate-fadeIn pb-12">
      
      {/* Toast Notification */}
      {successToast && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-600 text-white px-5 py-3.5 rounded-2xl shadow-xl flex items-center gap-3 animate-slideUp">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span className="text-xs sm:text-sm font-bold">{successToast}</span>
          <button onClick={() => setSuccessToast(null)} className="p-1 hover:bg-emerald-700 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Global Error Banner */}
      {errorMsg && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center justify-between text-red-800">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
            <p className="text-xs sm:text-sm font-medium">{errorMsg}</p>
          </div>
          <button onClick={() => setErrorMsg(null)} className="p-1 hover:bg-red-100 rounded-lg text-red-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 1. HEADER & CAREER STATUS BANNER */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-slate-900/10 relative overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-10 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-xs font-semibold text-blue-200">
              <Compass className="w-3.5 h-3.5 text-blue-300" />
              <span>Student Career Workspace • Phase 3.3</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
              Career Workspace & Target Roles
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Define your target industry benchmark, inspect canonical skill requirements, and anchor your personalized milestone roadmap.
            </p>
          </div>

          {/* Quick Metrics Capsule */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="bg-white/10 backdrop-blur-md border border-white/15 px-4 py-3 rounded-2xl flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/30 border border-blue-400/40 flex items-center justify-center text-blue-300">
                <Target className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs text-blue-200 font-medium">Career Goal</div>
                <div className="text-sm font-bold text-white">
                  {currentTarget ? 'Target Selected' : 'Not Selected'}
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md border border-white/15 px-4 py-3 rounded-2xl flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs text-indigo-200 font-medium">Available Roles</div>
                <div className="text-sm font-bold text-white">
                  {careerRoles.length} Active Tracks
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. "MY CAREER GOAL" SHOWCASE SECTION */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-soft space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              <span>My Active Target Career Goal</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              The benchmark role that drives automated skill gap analysis, recommended milestones, and opportunity matching.
            </p>
          </div>

          {currentTarget && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Active Benchmark
            </span>
          )}
        </div>

        {currentTarget ? (
          <div className="bg-gradient-to-br from-blue-50/70 via-indigo-50/40 to-slate-50 border border-blue-100 rounded-2xl p-6 space-y-5">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-xl font-black text-slate-900">{currentTarget.title}</h3>
                  <span className="px-2.5 py-0.5 rounded-lg bg-blue-600 text-white text-[11px] font-bold uppercase tracking-wider">
                    {currentTarget.industry_domain}
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
                  {currentTarget.description || 'Target career benchmark configured for your academic journey.'}
                </p>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <Button
                  onClick={() => handleOpenRoleDetail(currentTarget.id)}
                  variant="outline"
                  size="sm"
                  className="bg-white"
                >
                  <BookOpen className="w-3.5 h-3.5 mr-1.5" />
                  <span>View All Required Skills</span>
                </Button>
              </div>
            </div>

            {/* Required Skills Highlights */}
            {currentTarget.required_skills && currentTarget.required_skills.length > 0 && (
              <div className="pt-4 border-t border-blue-100/80 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-slate-700">
                  <span>Required Skills Overview ({currentTarget.required_skills.length} Total Competencies):</span>
                  <span className="text-blue-600 font-medium">
                    {currentTarget.required_skills.filter((s) => s.importance_level === 'CORE').length} Core •{' '}
                    {currentTarget.required_skills.filter((s) => s.importance_level !== 'CORE').length} Recommended
                  </span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {currentTarget.required_skills.map((skill) => (
                    <div
                      key={skill.skill_id}
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border transition-all ${
                        skill.importance_level === 'CORE'
                          ? 'bg-rose-50 border-rose-200 text-rose-800'
                          : 'bg-white border-slate-200 text-slate-700 shadow-2xs'
                      }`}
                    >
                      <span className="font-bold">{skill.skill_name}</span>
                      <span className={`text-[10px] uppercase font-bold px-1.5 py-0.2 rounded ${
                        skill.importance_level === 'CORE' ? 'bg-rose-200 text-rose-900' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {skill.required_level}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Career Direction Footer */}
            <div className="pt-3 border-t border-blue-100/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-600">
              <div className="flex items-center gap-2 text-slate-500">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Synchronized with Module 08 Skill Assessment and Module 09 Opportunities.</span>
              </div>
              <div className="flex items-center gap-3 font-semibold text-blue-600">
                <Link to="/student/assessments" className="hover:underline flex items-center gap-1">
                  <span>Take Skill Assessment</span>
                  <ChevronRight className="w-3 h-3" />
                </Link>
                <Link to="/student/skill-gaps" className="hover:underline flex items-center gap-1">
                  <span>Analyze Skill Gaps</span>
                  <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-8 sm:p-10 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/50 text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto shadow-2xs">
              <Target className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900">No Target Career Role Selected Yet</h3>
              <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
                Explore the active career roles below and select your dream trajectory to enable real-time competency benchmarking.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 3. EXPLORE CAREER ROLES CATALOG */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-soft space-y-6">
        
        {/* Title & Filters */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Compass className="w-5 h-5 text-blue-600" />
                <span>Explore Career Roles</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Browse canonical industry tracks directly backed by the PostgreSQL career benchmark repository.
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              Showing {filteredRoles.length} of {careerRoles.length} roles
            </span>
          </div>

          {/* Search & Domain Filter Bar */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search career roles by title, domain, or keywords..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 transition-all placeholder:text-slate-400 bg-slate-50/50"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Domain Filter Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 custom-scrollbar">
              <button
                onClick={() => setSelectedDomain('ALL')}
                className={`px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedDomain === 'ALL'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                All Domains
              </button>
              {availableDomains.map((domain) => (
                <button
                  key={domain}
                  onClick={() => setSelectedDomain(domain)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                    selectedDomain === domain
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {domain}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Roles Grid */}
        {filteredRoles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
            {filteredRoles.map((role) => {
              const isTarget = Boolean(role.is_current_target);

              return (
                <div
                  key={role.id}
                  className={`rounded-2xl border p-5 sm:p-6 transition-all flex flex-col justify-between relative group ${
                    isTarget
                      ? 'bg-gradient-to-b from-blue-50/80 to-white border-blue-400 shadow-md ring-1 ring-blue-400/50'
                      : 'bg-white border-slate-200/90 hover:border-blue-300 hover:shadow-soft'
                  }`}
                >
                  <div className="space-y-3">
                    {/* Top Badges */}
                    <div className="flex items-center justify-between gap-2">
                      <span className="px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 text-[10px] font-bold uppercase tracking-wider">
                        {role.industry_domain}
                      </span>
                      {isTarget && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg bg-emerald-600 text-white text-[10px] font-bold">
                          <Check className="w-3 h-3" />
                          <span>Target Goal</span>
                        </span>
                      )}
                    </div>

                    {/* Title & Description */}
                    <div>
                      <h4 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                        {role.title}
                      </h4>
                      <p className="text-xs text-slate-500 mt-1.5 leading-relaxed line-clamp-2">
                        {role.description || 'Industry-standard career track with specialized required skill requirements.'}
                      </p>
                    </div>

                    {/* Skill Count Chips */}
                    <div className="pt-2 flex items-center gap-2 text-xs">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-semibold text-[11px]">
                        <Layers className="w-3 h-3 text-slate-500" />
                        <span>{role.skills_count} Required Skills</span>
                      </span>
                      {role.core_skills_count > 0 && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-rose-50 text-rose-700 font-bold text-[10px]">
                          {role.core_skills_count} Core
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-5 mt-4 border-t border-slate-100 flex items-center justify-between gap-2">
                    <button
                      onClick={() => handleOpenRoleDetail(role.id)}
                      className="text-xs font-bold text-slate-700 hover:text-blue-600 flex items-center gap-1 py-1 transition-colors"
                    >
                      <span>View Skills</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>

                    {isTarget ? (
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600 px-3 py-1.5 rounded-xl bg-emerald-50">
                        <Check className="w-3.5 h-3.5" />
                        <span>Selected</span>
                      </span>
                    ) : (
                      <Button
                        onClick={() => handleSelectTargetRole(role.id)}
                        disabled={savingTarget}
                        variant="primary"
                        size="sm"
                        className="rounded-xl text-xs font-bold"
                      >
                        <span>Set as Goal</span>
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-10 rounded-2xl border border-dashed border-slate-200 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <Search className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">No Career Roles Found</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                No active career roles match your search term or domain filter.
              </p>
            </div>
            <Button
              onClick={() => {
                setSearchTerm('');
                setSelectedDomain('ALL');
              }}
              variant="outline"
              size="sm"
            >
              Clear Filters
            </Button>
          </div>
        )}
      </div>

      {/* 4. CAREER ROLE DETAILS MODAL */}
      {detailModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={() => setDetailModalOpen(false)}
          />

          {/* Modal Card */}
          <div className="relative bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-6 z-10 max-h-[90vh] overflow-y-auto custom-scrollbar animate-scaleUp">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="px-2.5 py-0.5 rounded-lg bg-blue-100 text-blue-800 text-[10px] font-bold uppercase tracking-wider">
                    {selectedRoleDetail?.industry_domain || 'Domain Track'}
                  </span>
                  {selectedRoleDetail?.is_current_target && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-600 text-white text-[10px] font-bold">
                      <Check className="w-3 h-3" />
                      <span>Current Target</span>
                    </span>
                  )}
                </div>
                <h3 className="text-xl sm:text-2xl font-black text-slate-900">
                  {selectedRoleDetail?.title}
                </h3>
              </div>

              <button
                onClick={() => setDetailModalOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {detailLoading ? (
              <div className="py-12 text-center">
                <Loading message="Loading required skills..." />
              </div>
            ) : selectedRoleDetail ? (
              <div className="space-y-6">
                
                {/* Description */}
                <div className="space-y-1.5">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Role Description
                  </h4>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                    {selectedRoleDetail.description || 'Standard industry career benchmark role.'}
                  </p>
                </div>

                {/* Required Skills Matrix */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-blue-600" />
                      <span>Required Skills Hierarchy ({selectedRoleDetail.required_skills?.length || 0})</span>
                    </h4>
                    <span className="text-[11px] text-slate-500 font-medium">
                      Canonical Module 08 Skill Taxonomy
                    </span>
                  </div>

                  {selectedRoleDetail.required_skills && selectedRoleDetail.required_skills.length > 0 ? (
                    <div className="space-y-2.5">
                      {selectedRoleDetail.required_skills.map((skill, sIdx) => {
                        const isCore = skill.importance_level === 'CORE';

                        return (
                          <div
                            key={skill.skill_id || sIdx}
                            className={`p-3.5 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                              isCore
                                ? 'bg-rose-50/40 border-rose-200/80'
                                : 'bg-slate-50/70 border-slate-200/80'
                            }`}
                          >
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-xs sm:text-sm text-slate-900">
                                  {skill.skill_name}
                                </span>
                                <span className="text-[10px] text-slate-500 font-medium bg-white px-2 py-0.5 rounded-md border border-slate-200">
                                  {skill.category}
                                </span>
                              </div>
                              {skill.description && (
                                <p className="text-[11px] text-slate-500 leading-tight line-clamp-1">
                                  {skill.description}
                                </p>
                              )}
                            </div>

                            <div className="flex items-center gap-2 shrink-0">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                isCore ? 'bg-rose-600 text-white' : 'bg-blue-600 text-white'
                              }`}>
                                {skill.importance_level}
                              </span>
                              <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-800 text-[10px] font-bold uppercase">
                                {skill.required_level}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="p-6 rounded-xl border border-dashed border-slate-200 text-center text-xs text-slate-500">
                      No skill requirements currently linked to this role.
                    </div>
                  )}
                </div>

                {/* Modal Footer / Set as Goal Action */}
                <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-3">
                  <Button
                    onClick={() => setDetailModalOpen(false)}
                    variant="outline"
                    size="md"
                  >
                    Close
                  </Button>

                  {selectedRoleDetail.is_current_target ? (
                    <div className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
                      <Check className="w-4 h-4" />
                      <span>This is your current Target Career Goal</span>
                    </div>
                  ) : (
                    <Button
                      onClick={() => handleSelectTargetRole(selectedRoleDetail.id)}
                      disabled={savingTarget}
                      variant="primary"
                      size="md"
                      className="shadow-md"
                    >
                      {savingTarget ? (
                        <span>Saving Target...</span>
                      ) : (
                        <>
                          <Target className="w-4 h-4 mr-1.5" />
                          <span>Set as My Target Career Goal</span>
                        </>
                      )}
                    </Button>
                  )}
                </div>

              </div>
            ) : null}

          </div>
        </div>
      )}

    </div>
  );
}
