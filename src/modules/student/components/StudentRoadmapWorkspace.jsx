import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Compass, 
  Target, 
  CheckCircle2, 
  Clock, 
  PlayCircle, 
  ExternalLink, 
  RefreshCw, 
  AlertCircle, 
  ChevronRight, 
  Layers, 
  BookOpen, 
  Award, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import api from '../../../lib/api';
import Button from '../../../components/Button';
import Loading from '../../../components/Loading';

export default function StudentRoadmapWorkspace() {
  const [roadmapOverview, setRoadmapOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [updatingItemId, setUpdatingItemId] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  const fetchRoadmap = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const res = await api.get('/student/roadmap');
      setRoadmapOverview(res.data);
    } catch (err) {
      console.error('Failed to load roadmap:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load career roadmap.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleGenerateRoadmap = async () => {
    try {
      setGenerating(true);
      setErrorMsg(null);
      const res = await api.post('/student/roadmap/generate');
      setRoadmapOverview(res.data);
      setSuccessToast('Personalized career roadmap successfully generated!');
      setTimeout(() => setSuccessToast(null), 4000);
    } catch (err) {
      console.error('Failed to generate roadmap:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to generate roadmap.');
    } finally {
      setGenerating(false);
    }
  };

  const handleUpdateItemStatus = async (itemId, newStatus) => {
    try {
      setUpdatingItemId(itemId);
      await api.put(`/student/roadmap/items/${itemId}`, { status: newStatus });
      // Refresh roadmap metrics
      const res = await api.get('/student/roadmap');
      setRoadmapOverview(res.data);
      setSuccessToast(`Step status updated to ${newStatus.replace('_', ' ')}.`);
      setTimeout(() => setSuccessToast(null), 3000);
    } catch (err) {
      console.error('Failed to update step status:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to update step status.');
    } finally {
      setUpdatingItemId(null);
    }
  };

  if (loading) {
    return <Loading label="Loading career roadmap..." />;
  }

  const hasTargetRole = roadmapOverview?.has_target_role;
  const hasActiveRoadmap = roadmapOverview?.has_active_roadmap;
  const targetRole = roadmapOverview?.target_career_role;
  const roadmap = roadmapOverview?.roadmap;
  const items = roadmap?.items || [];
  const totalSteps = roadmapOverview?.total_steps || 0;
  const completedSteps = roadmapOverview?.completed_steps || 0;
  const totalHours = roadmapOverview?.total_estimated_hours || 0;
  const completionPct = roadmapOverview?.completion_percentage || 0;

  return (
    <div className="space-y-6">
      {/* Notifications */}
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
          <button onClick={() => setErrorMsg(null)} className="text-rose-500 hover:text-rose-700 font-bold">
            ×
          </button>
        </div>
      )}

      {/* Workspace Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl">
                <Compass className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">Milestone Career Roadmap</h1>
                <p className="text-sm text-slate-500">
                  Step-by-step learning progression tailored to bridge your target role skill gaps.
                </p>
              </div>
            </div>
          </div>

          {hasTargetRole && (
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerateRoadmap}
                loading={generating}
                icon={<RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />}
              >
                {hasActiveRoadmap ? 'Sync & Regenerate' : 'Generate Roadmap'}
              </Button>
            </div>
          )}
        </div>

        {/* Progress & Target Role Info */}
        {hasTargetRole && targetRole && (
          <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Target Role</span>
              <div className="flex items-center space-x-2 mt-1">
                <Target className="w-4 h-4 text-blue-600 flex-shrink-0" />
                <span className="font-bold text-slate-900 truncate">{targetRole.title}</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Roadmap Progress</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-lg font-bold text-slate-900">{completionPct}%</span>
                <span className="text-xs text-slate-500 font-medium">{completedSteps} / {totalSteps} Steps</span>
              </div>
              <div className="w-full bg-slate-200 h-2 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-blue-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${completionPct}%` }}
                />
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Estimated Study Time</span>
              <div className="flex items-center space-x-2 mt-1">
                <Clock className="w-4 h-4 text-amber-500 flex-shrink-0" />
                <span className="text-lg font-bold text-slate-900">{totalHours} Hours</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Roadmap Status</span>
              <div className="flex items-center space-x-2 mt-1">
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                  Active Progression
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* State 1: No Target Career Role Selected */}
      {!hasTargetRole && (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center max-w-xl mx-auto my-8 shadow-sm">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Target className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Select a Target Career Goal First</h2>
          <p className="text-slate-600 mt-2 text-sm leading-relaxed">
            Your career roadmap is generated deterministically based on the specific required skills of your target role. Visit the Career Workspace to choose your goal.
          </p>
          <div className="mt-6">
            <Link to="/student/careers">
              <Button icon={<ArrowRight className="w-4 h-4" />}>
                Explore Career Roles
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* State 2: Target Role Selected but Roadmap Not Generated */}
      {hasTargetRole && !hasActiveRoadmap && (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center max-w-xl mx-auto my-8 shadow-sm">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Generate Your Roadmap for {targetRole?.title}</h2>
          <p className="text-slate-600 mt-2 text-sm leading-relaxed">
            Click below to build your milestone learning path featuring required skills, study hour estimates, and step-by-step progress tracking.
          </p>
          <div className="mt-6">
            <Button
              onClick={handleGenerateRoadmap}
              loading={generating}
              icon={<Compass className="w-4 h-4" />}
            >
              Build My Roadmap Now
            </Button>
          </div>
        </div>
      )}

      {/* State 3: Active Roadmap Checkpoints List */}
      {hasActiveRoadmap && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Layers className="w-5 h-5 text-blue-600" />
              <span>Learning Milestone Checkpoints ({items.length})</span>
            </h2>
            <span className="text-xs text-slate-500 font-medium">Sequential Skill Progression</span>
          </div>

          <div className="space-y-4">
            {items.map((item, idx) => {
              const isCompleted = item.status === 'COMPLETED';
              const isInProgress = item.status === 'IN_PROGRESS';
              const isUpdating = updatingItemId === item.id;

              return (
                <div
                  key={item.id}
                  className={`border rounded-xl p-5 transition-all ${
                    isCompleted
                      ? 'border-emerald-200 bg-emerald-50/30'
                      : isInProgress
                      ? 'border-blue-300 bg-blue-50/20 shadow-sm'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="flex items-start space-x-4">
                      {/* Step Badge */}
                      <div
                        className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm flex-shrink-0 ${
                          isCompleted
                            ? 'bg-emerald-600 text-white'
                            : isInProgress
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : idx + 1}
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                          <h3 className="font-bold text-slate-900 text-base">{item.title}</h3>
                          {item.skill && (
                            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                              {item.skill.name}
                            </span>
                          )}
                          {item.estimated_hours && (
                            <span className="inline-flex items-center text-xs font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                              <Clock className="w-3 h-3 mr-1 text-slate-400" />
                              {item.estimated_hours}h
                            </span>
                          )}
                        </div>

                        {item.description && (
                          <p className="text-sm text-slate-600 leading-relaxed">{item.description}</p>
                        )}

                        {item.resource_url && (
                          <div className="pt-1">
                            <a
                              href={item.resource_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800 space-x-1"
                            >
                              <span>Official Learning Documentation</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Status & Actions */}
                    <div className="flex items-center space-x-2 self-end md:self-auto flex-shrink-0">
                      {isCompleted ? (
                        <div className="flex items-center space-x-2">
                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 flex items-center">
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                            Completed
                          </span>
                          <button
                            onClick={() => handleUpdateItemStatus(item.id, 'IN_PROGRESS')}
                            disabled={isUpdating}
                            className="text-xs text-slate-400 hover:text-slate-600 font-medium underline px-1"
                          >
                            Reopen
                          </button>
                        </div>
                      ) : isInProgress ? (
                        <div className="flex items-center space-x-2">
                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 flex items-center">
                            <PlayCircle className="w-3.5 h-3.5 mr-1" />
                            In Progress
                          </span>
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleUpdateItemStatus(item.id, 'COMPLETED')}
                            loading={isUpdating}
                            icon={<CheckCircle2 className="w-3.5 h-3.5" />}
                          >
                            Mark Complete
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleUpdateItemStatus(item.id, 'IN_PROGRESS')}
                          loading={isUpdating}
                          icon={<PlayCircle className="w-3.5 h-3.5" />}
                        >
                          Start Step
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
