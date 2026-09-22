import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Target, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  Sparkles, 
  ArrowRight, 
  BookOpen, 
  Layers, 
  Compass,
  Zap,
  Filter
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentSkillGapWorkspace() {
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('ALL');

  const fetchSkillGaps = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/student/skill-gaps');
      setGapData(res.data || null);
    } catch (err) {
      console.error('Failed to fetch student skill gaps:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to calculate competency gap analysis.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillGaps();
  }, []);

  if (loading) {
    return <Loading label="Calculating competency gap variance against target career role..." />;
  }

  const hasTargetRole = gapData?.has_target_role && gapData?.target_career_role;
  const targetRole = gapData?.target_career_role;
  const summary = gapData?.summary || { satisfied_count: 0, insufficient_count: 0, missing_count: 0, total_required: 0 };
  const gaps = gapData?.gaps || [];

  const compatibilityPct = summary.total_required > 0 
    ? Math.round((summary.satisfied_count / summary.total_required) * 100) 
    : 0;

  const filteredGaps = gaps.filter((g) => {
    if (selectedFilter === 'ALL') return true;
    return g.gap_status === selectedFilter;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'SATISFIED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Satisfied</span>
          </span>
        );
      case 'INSUFFICIENT':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Level Gap</span>
          </span>
        );
      case 'MISSING':
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
            <span>Missing Skill</span>
          </span>
        );
    }
  };

  const getImportanceBadge = (importance) => {
    if (importance === 'CORE') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 uppercase">
          Core Requirement
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600 uppercase">
        Recommended
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchSkillGaps}>
            Retry
          </Button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100">
              <TrendingUp className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Competency Gap Analysis</h1>
              <p className="text-sm text-slate-500">
                Real-time variance calculation between your assessed skill passport and target role requirements.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Link to="/student/careers">
              <Button variant="outline" size="sm" icon={<Compass className="w-4 h-4" />}>
                {hasTargetRole ? 'Change Target Role' : 'Select Target Role'}
              </Button>
            </Link>
            <Link to="/student/roadmaps">
              <Button variant="primary" size="sm" icon={<BookOpen className="w-4 h-4" />}>
                View Roadmap
              </Button>
            </Link>
          </div>
        </div>

        {/* Target Role Status Card */}
        {!hasTargetRole ? (
          <div className="p-6 bg-slate-50 rounded-2xl border border-dashed border-slate-300 text-center space-y-3">
            <Target className="w-10 h-10 text-slate-400 mx-auto" />
            <h3 className="text-base font-bold text-slate-900">No Target Career Role Selected</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Select a target career role to calculate your personalized skill gap variance, missing core competencies, and custom roadmap.
            </p>
            <Link to="/student/careers" className="inline-block pt-1">
              <Button variant="primary" size="sm" icon={<ArrowRight className="w-4 h-4" />}>
                Explore Career Roles
              </Button>
            </Link>
          </div>
        ) : (
          <div className="p-5 bg-gradient-to-r from-blue-900 to-indigo-900 rounded-2xl text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-white/10 text-blue-200 border border-white/10">
                Target Role Benchmark
              </span>
              <h2 className="text-xl font-bold text-white pt-1">{targetRole.title}</h2>
              <p className="text-xs text-blue-200">
                Industry Domain: <span className="text-white font-medium">{targetRole.industry_domain}</span>
              </p>
            </div>

            <div className="flex items-center space-x-4 bg-white/10 px-5 py-3 rounded-xl backdrop-blur-sm border border-white/10">
              <div className="text-center">
                <span className="block text-[10px] font-bold text-blue-200 uppercase tracking-wider">Role Compatibility</span>
                <strong className="text-2xl font-extrabold text-white">{compatibilityPct}%</strong>
              </div>
            </div>
          </div>
        )}

        {/* Summary Metrics Bar */}
        {hasTargetRole && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
              <span className="block text-xs font-semibold text-slate-400 uppercase">Required Skills</span>
              <span className="text-2xl font-bold text-slate-900">{summary.total_required}</span>
            </div>

            <div className="p-4 bg-emerald-50/50 rounded-xl border border-emerald-100 text-center">
              <span className="block text-xs font-semibold text-emerald-700 uppercase">Satisfied</span>
              <span className="text-2xl font-bold text-emerald-700">{summary.satisfied_count}</span>
            </div>

            <div className="p-4 bg-amber-50/50 rounded-xl border border-amber-100 text-center">
              <span className="block text-xs font-semibold text-amber-700 uppercase">Level Gap</span>
              <span className="text-2xl font-bold text-amber-700">{summary.insufficient_count}</span>
            </div>

            <div className="p-4 bg-rose-50/50 rounded-xl border border-rose-100 text-center">
              <span className="block text-xs font-semibold text-rose-700 uppercase">Missing Skills</span>
              <span className="text-2xl font-bold text-rose-700">{summary.missing_count}</span>
            </div>
          </div>
        )}
      </div>

      {/* Filter Tabs */}
      {hasTargetRole && (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-bold text-slate-500 uppercase">Filter Gaps:</span>
          </div>

          <div className="flex items-center space-x-2 overflow-x-auto">
            {[
              { id: 'ALL', label: `All Requirements (${gaps.length})` },
              { id: 'MISSING', label: `Missing (${summary.missing_count})` },
              { id: 'INSUFFICIENT', label: `Level Gaps (${summary.insufficient_count})` },
              { id: 'SATISFIED', label: `Satisfied (${summary.satisfied_count})` },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedFilter(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedFilter === tab.id
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Gaps List / Grid */}
      {hasTargetRole && (
        <>
          {filteredGaps.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center space-y-2 shadow-sm">
              <p className="text-slate-600 font-medium text-sm">No skill gaps match the selected filter.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredGaps.map((gap, idx) => {
                const gapScoreVal = Number(gap.gap_score || 0);

                return (
                  <div
                    key={gap.skill_id || idx}
                    className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-md hover:border-blue-300 transition-all space-y-4 flex flex-col justify-between"
                  >
                    <div className="space-y-3">
                      {/* Top Badges */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                            {gap.category || 'General'}
                          </span>
                          {getImportanceBadge(gap.importance_level)}
                        </div>

                        {getStatusBadge(gap.gap_status)}
                      </div>

                      {/* Skill Name */}
                      <h3 className="text-lg font-bold text-slate-900">{gap.skill_name}</h3>

                      {/* Proficiency Variance Comparison */}
                      <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between text-xs">
                        <div>
                          <span className="block text-[10px] font-semibold text-slate-400 uppercase">Current Level</span>
                          <span className={`font-bold ${gap.current_level === 'NONE' ? 'text-rose-600' : 'text-slate-800'}`}>
                            {gap.current_level}
                          </span>
                        </div>

                        <ArrowRight className="w-4 h-4 text-slate-400 flex-shrink-0" />

                        <div className="text-right">
                          <span className="block text-[10px] font-semibold text-slate-400 uppercase">Required Level</span>
                          <span className="font-bold text-blue-700">{gap.target_level}</span>
                        </div>
                      </div>

                      {/* Variance Score */}
                      {gapScoreVal > 0 && (
                        <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                          <span>Competency Gap Variance</span>
                          <span className="font-bold text-rose-600">+{gapScoreVal.toFixed(1)} level steps</span>
                        </div>
                      )}
                    </div>

                    {/* Footer Actions */}
                    <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                      {gap.gap_status !== 'SATISFIED' ? (
                        <>
                          <Link to="/student/assessments">
                            <Button variant="outline" size="sm" icon={<Zap className="w-3.5 h-3.5 text-amber-500" />}>
                              Take Assessment
                            </Button>
                          </Link>
                          <Link to="/student/roadmaps">
                            <Button variant="primary" size="sm" icon={<BookOpen className="w-3.5 h-3.5" />}>
                              View Roadmap
                            </Button>
                          </Link>
                        </>
                      ) : (
                        <span className="text-xs font-semibold text-emerald-600 flex items-center space-x-1">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Meets Target Requirement</span>
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
