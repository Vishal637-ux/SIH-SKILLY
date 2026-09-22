import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  CheckCheck, 
  Clock, 
  Filter, 
  MessageSquare, 
  Users, 
  Briefcase, 
  Award, 
  Sparkles, 
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Inbox
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import Button from './Button';

export default function NotificationCenter({ userRole = 'STUDENT' }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [filterUnread, setFilterUnread] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [markingAll, setMarkingAll] = useState(false);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      const url = filterUnread ? '/notifications?unread_only=true' : '/notifications';
      const res = await api.get(url);
      setNotifications(res.data.items || []);
      setUnreadCount(res.data.unread_count || 0);
      setTotalCount(res.data.total_count || 0);
    } catch (err) {
      console.error('Failed to load notifications:', err);
      setError(err.response?.data?.detail || 'Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [filterUnread]);

  const handleMarkAsRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      setMarkingAll(true);
      await api.put('/notifications/read-all');
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      );
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    } finally {
      setMarkingAll(false);
    }
  };

  const getIconForType = (type) => {
    switch (type?.toUpperCase()) {
      case 'MENTORSHIP':
        return <Users className="w-5 h-5 text-indigo-600" />;
      case 'APPLICATION':
      case 'INTERNSHIP':
      case 'PLACEMENT':
        return <Briefcase className="w-5 h-5 text-emerald-600" />;
      case 'COMMUNITY':
      case 'POST':
      case 'COMMENT':
        return <MessageSquare className="w-5 h-5 text-blue-600" />;
      case 'SKILL':
      case 'ASSESSMENT':
        return <Award className="w-5 h-5 text-amber-600" />;
      case 'SYSTEM':
      default:
        return <Sparkles className="w-5 h-5 text-purple-600" />;
    }
  };

  const getDestinationForRef = (type, refType) => {
    const t = (refType || type || '').toUpperCase();
    if (t.includes('MENTOR')) {
      return userRole === 'ALUMNI' ? '/alumni/requests' : '/student/mentorship';
    }
    if (t.includes('APP') || t.includes('INTERN') || t.includes('OPPORTUNITY')) {
      return userRole === 'INDUSTRY' ? '/industry/applications' : '/student/applications';
    }
    if (t.includes('COMMUNITY') || t.includes('POST') || t.includes('COMMENT')) {
      return '/community';
    }
    if (t.includes('SKILL') || t.includes('ASSESSMENT')) {
      return '/student/assessments';
    }
    return null;
  };

  const formatTimestamp = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const diffMs = now - d;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      
      {/* Top Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center relative shrink-0">
            <Bell className="w-6 h-6" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center border-2 border-white">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">Notification Center</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              {unreadCount > 0
                ? `You have ${unreadCount} unread alert${unreadCount > 1 ? 's' : ''}`
                : 'All caught up! No unread notifications.'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
          <button
            onClick={fetchNotifications}
            disabled={loading}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors border border-slate-200"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          {unreadCount > 0 && (
            <Button
              onClick={handleMarkAllRead}
              disabled={markingAll || loading}
              variant="outline"
              size="sm"
              className="text-xs font-semibold"
            >
              <CheckCheck className="w-3.5 h-3.5 mr-1 text-blue-600" />
              <span>Mark All as Read</span>
            </Button>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterUnread(false)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              !filterUnread
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            All Notifications ({totalCount})
          </button>
          <button
            onClick={() => setFilterUnread(true)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              filterUnread
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <span>Unread Only</span>
            {unreadCount > 0 && (
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                filterUnread ? 'bg-white text-blue-600' : 'bg-red-500 text-white'
              }`}>
                {unreadCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Notifications List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200 p-5 animate-pulse flex gap-4">
              <div className="w-10 h-10 rounded-xl bg-slate-200 shrink-0" />
              <div className="space-y-2 flex-1">
                <div className="h-4 bg-slate-200 rounded w-1/3" />
                <div className="h-3 bg-slate-200 rounded w-3/4" />
              </div>
            </div>
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-md mx-auto space-y-3 shadow-sm">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
            <Inbox className="w-7 h-7" />
          </div>
          <h3 className="text-base font-bold text-slate-900">No Notifications</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            {filterUnread
              ? 'You have read all your notifications! Switch to "All Notifications" to view past alerts.'
              : 'You have no system or workflow notifications at this time.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const dest = getDestinationForRef(n.notification_type, n.reference_type);
            return (
              <div
                key={n.id}
                onClick={() => !n.is_read && handleMarkAsRead(n.id)}
                className={`group rounded-2xl border transition-all p-4 flex items-start gap-3.5 cursor-pointer relative ${
                  !n.is_read
                    ? 'bg-blue-50/40 border-blue-200/90 shadow-2xs hover:bg-blue-50/70'
                    : 'bg-white border-slate-200/80 hover:border-slate-300 hover:shadow-2xs'
                }`}
              >
                {/* Unread indicator dot */}
                {!n.is_read && (
                  <span className="absolute top-4 left-2.5 w-2 h-2 rounded-full bg-blue-600" />
                )}

                {/* Icon */}
                <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0 mt-0.5 group-hover:scale-105 transition-transform">
                  {getIconForType(n.notification_type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pr-4">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className={`text-sm ${!n.is_read ? 'font-bold text-slate-900' : 'font-semibold text-slate-800'}`}>
                      {n.title}
                    </h4>
                    <span className="text-[11px] font-medium text-slate-400 shrink-0 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatTimestamp(n.created_at)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed line-clamp-2">
                    {n.message}
                  </p>

                  {/* Actions / Destination Link */}
                  <div className="mt-2.5 flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[10px] font-bold uppercase tracking-wider">
                        {n.notification_type}
                      </span>
                    </div>

                    {dest && (
                      <Link
                        to={dest}
                        onClick={(e) => e.stopPropagation()}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        <span>View Details</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
