import React, { useState, useEffect, useMemo } from 'react';
import { 
  Trophy, 
  Sparkles, 
  Calendar, 
  Clock, 
  MapPin, 
  Search, 
  Filter, 
  Users, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  ArrowRight, 
  ExternalLink, 
  RefreshCw, 
  Award, 
  Layers, 
  ShieldCheck,
  BookOpen,
  Info
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
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return String(dateStr);
  }
};

export default function StudentCompetitionsWorkspace() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);

  // Search & Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [selectedItem, setSelectedItem] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [registeredIds, setRegisteredIds] = useState(new Set());

  const fetchCompetitions = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      // Canonical existing endpoint for campus & platform activities/competitions
      const res = await api.get('/community/activities');
      setActivities(res.data || []);
    } catch (err) {
      console.error('Failed to fetch competitions and activities:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to load competitions and hackathons catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompetitions();
  }, []);

  // Filtered competitions / activities
  const filteredItems = useMemo(() => {
    return activities.filter((item) => {
      const text = `${item.title} ${item.description} ${item.institution_name || ''} ${item.activity_type || ''} ${item.location_or_url || ''}`.toLowerCase();
      const matchesSearch = text.includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'ALL' || item.activity_type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [activities, searchTerm, typeFilter]);

  // Derived type options
  const activityTypes = useMemo(() => {
    const types = Array.from(new Set(activities.map(a => a.activity_type).filter(Boolean)));
    return ['ALL', ...types];
  }, [activities]);

  const handleRegister = (item) => {
    // Record local registered state
    setRegisteredIds((prev) => new Set(prev).add(item.id));
    setSuccessToast(`Successfully registered interest for "${item.title}"!`);
    setTimeout(() => setSuccessToast(null), 4000);
  };

  if (loading) {
    return <Loading label="Loading Competitions & Hackathons Catalog..." />;
  }

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {successToast && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-between shadow-lg backdrop-blur-md animate-fade-in">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span className="font-medium text-sm">{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-emerald-400 hover:text-emerald-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Error Alert */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-between shadow-lg backdrop-blur-md">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <span className="font-medium text-sm">{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-300">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/20 p-6 md:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
              <Trophy className="w-3.5 h-3.5 text-amber-400" />
              Module 11 — Competitions & Hackathons Engine
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              Competitions & Hackathons Workspace
            </h1>
            <p className="text-slate-400 text-sm md:text-base leading-relaxed">
              Discover collegiate hackathons, case competitions, technical challenges, and collaborative events across partner academic institutions.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <Button
              variant="outline"
              onClick={fetchCompetitions}
              className="border-slate-700 text-slate-300 hover:bg-slate-800/60"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Catalog
            </Button>
          </div>
        </div>

        {/* Quick Stats Bar */}
        <div className="mt-6 pt-6 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
            <div className="text-xs text-slate-400">Total Events</div>
            <div className="text-lg font-bold text-white mt-0.5">{activities.length}</div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
            <div className="text-xs text-slate-400">Inter-College Competitions</div>
            <div className="text-lg font-bold text-indigo-400 mt-0.5">
              {activities.filter(a => a.activity_type === 'HACKATHON' || a.activity_type === 'COMPETITION' || a.activity_type === 'CONTEST').length || activities.length}
            </div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
            <div className="text-xs text-slate-400">My Registrations</div>
            <div className="text-lg font-bold text-emerald-400 mt-0.5">{registeredIds.size}</div>
          </div>

          <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3">
            <div className="text-xs text-slate-400">Status</div>
            <div className="text-lg font-bold text-slate-200 mt-0.5">Active</div>
          </div>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search competitions, hackathons, organizers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <span className="text-xs text-slate-400 font-medium hidden md:inline">Category:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            {activityTypes.map((t) => (
              <option key={t} value={t}>
                {t === 'ALL' ? 'All Activity Categories' : t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Competition Cards Grid */}
      {filteredItems.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/40 border border-slate-800/60 rounded-2xl p-8">
          <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-300">No Competitions or Hackathons Found</h3>
          <p className="text-slate-500 text-sm mt-1 max-w-md mx-auto">
            Try adjusting your search criteria or category filter to explore upcoming campus challenges.
          </p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchTerm('');
              setTypeFilter('ALL');
            }}
            className="mt-5 border-slate-800 text-slate-300"
          >
            Reset Filters
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => {
            const isRegistered = registeredIds.has(item.id);

            return (
              <div
                key={item.id}
                className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 rounded-2xl p-6 flex flex-col justify-between space-y-4 transition-all duration-200 shadow-lg group"
              >
                <div className="space-y-3">
                  {/* Category Badge & Registration Status */}
                  <div className="flex items-start justify-between gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                      item.activity_type === 'HACKATHON' || item.activity_type === 'COMPETITION'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                    }`}>
                      {item.activity_type || 'COMPETITION'}
                    </span>

                    {isRegistered && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" />
                        Registered
                      </span>
                    )}
                  </div>

                  {/* Title & Host */}
                  <div>
                    <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span>{item.institution_name || 'Academic Institution'}</span>
                    </p>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-slate-300 leading-relaxed line-clamp-3 bg-slate-950/60 border border-slate-800/80 p-3 rounded-xl">
                    {item.description}
                  </p>

                  {/* Dates & Location */}
                  <div className="space-y-1.5 text-xs text-slate-400 pt-1">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span>Starts: {formatDate(item.start_time)}</span>
                    </div>

                    {item.location_or_url && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <span className="truncate">{item.location_or_url}</span>
                      </div>
                    )}

                    {item.conducted_by_name && (
                      <div className="flex items-center gap-2 text-slate-500">
                        <Users className="w-3.5 h-3.5 shrink-0" />
                        <span>Organized by: {item.conducted_by_name}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
                  <button
                    onClick={() => {
                      setSelectedItem(item);
                      setDetailModalOpen(true);
                    }}
                    className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                  >
                    View Details
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <Button
                    variant={isRegistered ? "outline" : "primary"}
                    onClick={() => handleRegister(item)}
                    disabled={isRegistered}
                    className={
                      isRegistered
                        ? "border-emerald-500/30 text-emerald-400 text-xs py-1.5 px-3"
                        : "bg-indigo-600 hover:bg-indigo-500 text-white text-xs py-1.5 px-3 shadow-md shadow-indigo-600/20"
                    }
                  >
                    {isRegistered ? "Registered" : "Register / Participate"}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* DETAIL MODAL */}
      {detailModalOpen && selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-5 p-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                <h3 className="text-lg font-bold text-white">Event & Challenge Details</h3>
              </div>
              <button
                onClick={() => {
                  setDetailModalOpen(false);
                  setSelectedItem(null);
                }}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-sm text-slate-300">
              <div>
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {selectedItem.activity_type || 'COMPETITION'}
                </span>
                <h2 className="text-xl font-bold text-white mt-2">{selectedItem.title}</h2>
                <p className="text-xs text-slate-400 mt-1">Host: {selectedItem.institution_name || 'Academic Institution'}</p>
              </div>

              <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Description & Guidelines</h4>
                <p className="text-slate-300 text-sm leading-relaxed">{selectedItem.description}</p>
              </div>

              <div className="space-y-2 bg-slate-950/40 border border-slate-800/80 p-4 rounded-xl text-xs">
                <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-400">Start Time:</span>
                  <span className="font-semibold text-slate-200">{formatDate(selectedItem.start_time)}</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-slate-800/60">
                  <span className="text-slate-400">End Time:</span>
                  <span className="font-semibold text-slate-200">{formatDate(selectedItem.end_time)}</span>
                </div>

                {selectedItem.location_or_url && (
                  <div className="flex items-center justify-between py-1">
                    <span className="text-slate-400">Venue / Link:</span>
                    <span className="font-semibold text-indigo-400">{selectedItem.location_or_url}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <Button
                variant="outline"
                onClick={() => {
                  setDetailModalOpen(false);
                  setSelectedItem(null);
                }}
                className="border-slate-800 text-slate-300"
              >
                Close
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  handleRegister(selectedItem);
                  setDetailModalOpen(false);
                  setSelectedItem(null);
                }}
                className="bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                Register Interest
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
