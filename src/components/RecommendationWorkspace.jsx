import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Target, 
  Award, 
  TrendingUp, 
  CheckCircle2, 
  AlertCircle, 
  ChevronRight, 
  RefreshCw,
  BookOpen,
  Briefcase,
  Users,
  Compass,
  Zap,
  Info
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import Button from './Button';

export default function RecommendationWorkspace() {
  const [overview, setOverview] = useState(null);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/student/recommendations');
      setOverview(res.data);
    } catch (err) {
      console.error('Failed to load AI recommendations:', err);
      setError(err.response?.data?.detail || 'Failed to generate recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const getScoreBadge = (score) => {
    if (score >= 80) {
      return (
        <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold flex items-center gap-1">
          <Zap className="w-3.5 h-3.5 text-emerald-600 fill-emerald-500" />
          <span>{score.toFixed(0)}% Match</span>
        </span>
      );
    }
    if (score >= 60) {
      return (
        <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>{score.toFixed(0)}% Fit</span>
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold flex items-center gap-1">
        <Info className="w-3.5 h-3.5 text-amber-600" />
        <span>{score.toFixed(0)}% Potential</span>
      </span>
    );
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'CAREER_ROLE':
        return <Compass className="w-5 h-5 text-indigo-600" />;
      case 'TRAINING_PROGRAM':
        return <BookOpen className="w-5 h-5 text-purple-600" />;
      case 'OPPORTUNITY':
        return <Briefcase className="w-5 h-5 text-emerald-600" />;
      case 'MENTOR':
        return <Users className="w-5 h-5 text-blue-600" />;
      default:
        return <Sparkles className="w-5 h-5 text-blue-600" />;
    }
  };

  const getAllItems = () => {
    if (!overview) return [];
    if (activeCategory === 'CAREER_ROLE') return overview.career_recommendations || [];
    if (activeCategory === 'TRAINING_PROGRAM') return overview.learning_recommendations || [];
    if (activeCategory === 'OPPORTUNITY') return overview.opportunity_recommendations || [];
    if (activeCategory === 'MENTOR') return overview.mentor_recommendations || [];

    // Combine top items for ALL
    const combined = [
      ...(overview.career_recommendations || []),
      ...(overview.learning_recommendations || []),
      ...(overview.opportunity_recommendations || []),
      ...(overview.mentor_recommendations || []),
    ];
    combined.sort((a, b) => b.score - a.score);
    return combined;
  };

  const itemsToDisplay = getAllItems();

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      
      {/* Top AI Spotlight Banner */}
      <div className="bg-gradient-to-br from-indigo-950 via-slate-900 to-blue-950 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Skill-Aware Recommendation Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              AI Career & Skill Recommendations
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Intelligent hybrid matchmaking connecting your verified skills, target role alignment, and active competency gaps to real opportunities.
            </p>

            {overview && (
              <div className="pt-2 flex flex-wrap items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 border border-white/15">
                  <Target className="w-4 h-4 text-blue-400" />
                  <span>Target Goal: <strong className="text-white">{overview.target_role_title || 'Not Set'}</strong></span>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 border border-white/15">
                  <Award className="w-4 h-4 text-emerald-400" />
                  <span>Assessed Skills: <strong className="text-white">{overview.assessed_skills_count}</strong></span>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 border border-white/15">
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  <span>Active Gaps: <strong className="text-white">{overview.active_gaps_count}</strong></span>
                </div>
              </div>
            )}
          </div>

          <div className="shrink-0 self-start md:self-auto">
            <button
              onClick={fetchRecommendations}
              disabled={loading}
              className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Recompute AI Match</span>
            </button>
          </div>

        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-slate-200">
        {[
          { id: 'ALL', label: 'All Recommendations' },
          { id: 'CAREER_ROLE', label: 'Career Roles' },
          { id: 'TRAINING_PROGRAM', label: 'Learning & Courses' },
          { id: 'OPPORTUNITY', label: 'Internships & Jobs' },
          { id: 'MENTOR', label: 'Alumni & Mentors' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveCategory(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              activeCategory === tab.id
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Recommendations Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200 p-6 animate-pulse space-y-4">
              <div className="h-6 bg-slate-200 rounded w-1/2" />
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-16 bg-slate-100 rounded" />
            </div>
          ))}
        </div>
      ) : itemsToDisplay.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-md mx-auto space-y-3 shadow-sm">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
            <Sparkles className="w-7 h-7" />
          </div>
          <h3 className="text-base font-bold text-slate-900">No Recommendations Available</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            Complete your academic profile or take a diagnostic skill assessment to enable intelligent career recommendations.
          </p>
          <div className="pt-2">
            <Button to="/student/assessments" variant="primary" size="sm">
              Take Skill Assessment
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {itemsToDisplay.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md hover:border-blue-200 transition-all flex flex-col justify-between space-y-5"
            >
              {/* Header: Icon, Category & Score */}
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0">
                      {getCategoryIcon(item.category)}
                    </div>
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        {item.category.replace('_', ' ')}
                      </span>
                      <h3 className="text-base font-bold text-slate-900 leading-snug">
                        {item.title}
                      </h3>
                    </div>
                  </div>
                  <div className="shrink-0">{getScoreBadge(item.score)}</div>
                </div>

                {item.organization_or_provider && (
                  <p className="text-xs font-semibold text-slate-500">
                    {item.organization_or_provider} {item.subtitle ? `• ${item.subtitle}` : ''}
                  </p>
                )}

                {/* Explainability Reason Callout */}
                <div className="p-3 rounded-xl bg-indigo-50/50 border border-indigo-100 text-xs text-indigo-900 leading-relaxed">
                  <strong className="font-semibold text-indigo-950">AI Insight: </strong>
                  {item.explanation}
                </div>

                {/* Matched Skills & Skill Gaps Chips */}
                <div className="space-y-2 pt-1">
                  {item.matched_skills && item.matched_skills.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider mr-1">
                        Matched:
                      </span>
                      {item.matched_skills.map((skill, sIdx) => (
                        <span
                          key={sIdx}
                          className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-medium flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>{skill}</span>
                        </span>
                      ))}
                    </div>
                  )}

                  {item.skill_gaps && item.skill_gaps.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider mr-1">
                        Gap Skills:
                      </span>
                      {item.skill_gaps.map((gap, gIdx) => (
                        <span
                          key={gIdx}
                          className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200 text-[11px] font-medium"
                        >
                          {gap}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400">
                  {item.eligibility ? 'Eligible' : 'Prerequisites Required'}
                </span>
                <Link
                  to={item.action_link}
                  className="inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-800 hover:underline"
                >
                  <span>Explore Recommendation</span>
                  <ChevronRight className="w-4 h-4" />
                </Link>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
