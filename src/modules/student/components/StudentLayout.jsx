import React, { useState, useEffect } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Compass, 
  Award, 
  Layers, 
  TrendingUp, 
  Target, 
  BookOpen, 
  Briefcase, 
  FileText, 
  Building2, 
  Users, 
  MessageSquare, 
  Trophy, 
  Sparkles, 
  Bot, 
  User, 
  Bell, 
  Menu, 
  X, 
  ChevronRight,
  GraduationCap
} from 'lucide-react';
import useAuth from '../../../hooks/useAuth';
import api from '../../../lib/api';

export default function StudentLayout({ children, activeViewTitle = "Dashboard" }) {
  const { user } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    let isMounted = true;
    const fetchUnread = async () => {
      try {
        const res = await api.get('/notifications/unread-count');
        if (isMounted) {
          setUnreadCount(res.data.unread_count || 0);
        }
      } catch (err) {
        // Silent catch for layout badge
      }
    };
    fetchUnread();
    return () => { isMounted = false; };
  }, [location.pathname]);

  const displayName = user?.profile?.first_name 
    ? `${user.profile.first_name} ${user.profile.last_name || ''}`.trim() 
    : user?.username || 'Student';

  // Navigation taxonomy grouped logically
  const navSections = [
    {
      title: 'Overview',
      items: [
        { name: 'Dashboard', path: '/student', icon: LayoutDashboard, exact: true },
        { name: 'Career Journey', path: '/student/journey', icon: Compass },
      ],
    },
    {
      title: 'Skills & Assessment',
      items: [
        { name: 'Skill Assessment', path: '/student/assessments', icon: Award },
        { name: 'Skill Profile', path: '/student/skills', icon: Layers },
        { name: 'Skill Gap Analysis', path: '/student/skill-gaps', icon: TrendingUp },
      ],
    },
    {
      title: 'Career & Learning',
      items: [
        { name: 'Career Explorer', path: '/student/careers', icon: Target },
        { name: 'Career Roadmap', path: '/student/roadmaps', icon: Compass },
        { name: 'Learning & Courses', path: '/student/learning', icon: BookOpen },
      ],
    },
    {
      title: 'Opportunities',
      items: [
        { name: 'Internships & Projects', path: '/student/internships', icon: Briefcase },
        { name: 'My Applications', path: '/student/applications', icon: FileText },
        { name: 'Placement Drives', path: '/student/placements', icon: Building2 },
      ],
    },
    {
      title: 'Growth & Network',
      items: [
        { name: 'Mentorship', path: '/student/mentorship', icon: Users },
        { name: 'Community', path: '/student/community', icon: MessageSquare },
        { name: 'Competitions', path: '/student/competitions', icon: Trophy },
      ],
    },
    {
      title: 'Portfolio & AI',
      items: [
        { name: 'Digital Portfolio', path: '/student/portfolio', icon: Layers },
        { name: 'Resume Versions', path: '/student/resume', icon: FileText },
        { name: 'Achievements', path: '/student/achievements', icon: Sparkles },
        { name: 'AI Career Support', path: '/student/ai-support', icon: Bot },
      ],
    },
    {
      title: 'Account',
      items: [
        { name: 'Profile & Academics', path: '/student/profile', icon: User },
        { name: 'Notifications', path: '/student/notifications', icon: Bell },
      ],
    },
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)] bg-slate-50 flex flex-col">
      
      {/* Top Student Navigation Header */}
      <div className="bg-white border-b border-slate-200 sticky top-16 sm:top-20 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          
          {/* Left: Mobile Sidebar Trigger & Breadcrumb */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 lg:hidden"
              aria-label="Open student sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Link to="/student" className="hover:text-blue-600 font-medium flex items-center gap-1">
                <GraduationCap className="w-3.5 h-3.5 text-blue-600" />
                <span>Student Hub</span>
              </Link>
              <ChevronRight className="w-3 h-3 text-slate-400" />
              <span className="font-bold text-slate-900 truncate max-w-[150px] sm:max-w-none">
                {activeViewTitle}
              </span>
            </div>
          </div>

          {/* Right: User Role & Quick Actions */}
          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              to="/student/notifications"
              className="p-2 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-xl transition-colors relative"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500 ring-2 ring-white" />
              )}
            </Link>

            <Link
              to="/student/profile"
              className="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-slate-100 hover:bg-blue-50 border border-slate-200 text-xs font-semibold text-slate-800 transition-colors"
            >
              <div className="w-6 h-6 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-[11px]">
                {displayName ? displayName[0].toUpperCase() : 'S'}
              </div>
              <span className="hidden sm:inline-block truncate max-w-[120px]">{displayName}</span>
              <span className="px-1.5 py-0.2 rounded bg-blue-600 text-white text-[9px] font-bold">
                STUDENT
              </span>
            </Link>
          </div>

        </div>
      </div>

      {/* Main Container with Sidebar + Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-1 flex gap-6">
        
        {/* Desktop Left Sidebar */}
        <aside className="hidden lg:block w-64 shrink-0">
          <div className="bg-white rounded-2xl border border-slate-200/80 p-4 shadow-soft sticky top-36 space-y-6 max-h-[calc(100vh-10rem)] overflow-y-auto custom-scrollbar">
            {navSections.map((section, sIdx) => (
              <div key={sIdx} className="space-y-1">
                <h3 className="px-3 text-[10px] font-black uppercase tracking-wider text-slate-400">
                  {section.title}
                </h3>
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = item.exact 
                    ? location.pathname === item.path 
                    : location.pathname.startsWith(item.path);

                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      end={item.exact}
                      className={({ isActive: linkActive }) =>
                        `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                          linkActive || isActive
                            ? 'bg-blue-600 text-white shadow-xs'
                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                        }`
                      }
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      <span className="truncate">{item.name}</span>
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </div>
        </aside>

        {/* Mobile Left Sidebar Drawer */}
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            {/* Backdrop */}
            <div 
              className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
              onClick={() => setMobileOpen(false)}
            />
            {/* Drawer */}
            <div className="fixed inset-y-0 left-0 max-w-xs w-full bg-white shadow-2xl p-5 overflow-y-auto space-y-6 flex flex-col justify-between animate-slideRight">
              <div className="space-y-6">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <GraduationCap className="w-6 h-6 text-blue-600" />
                    <span className="font-bold text-slate-900">Student Navigation</span>
                  </div>
                  <button
                    onClick={() => setMobileOpen(false)}
                    className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {navSections.map((section, sIdx) => (
                  <div key={sIdx} className="space-y-1">
                    <h3 className="px-3 text-[10px] font-black uppercase tracking-wider text-slate-400">
                      {section.title}
                    </h3>
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      const isActive = item.exact 
                        ? location.pathname === item.path 
                        : location.pathname.startsWith(item.path);

                      return (
                        <NavLink
                          key={item.path}
                          to={item.path}
                          end={item.exact}
                          onClick={() => setMobileOpen(false)}
                          className={({ isActive: linkActive }) =>
                            `flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                              linkActive || isActive
                                ? 'bg-blue-600 text-white'
                                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                            }`
                          }
                        >
                          <Icon className="w-4 h-4 shrink-0" />
                          <span className="truncate">{item.name}</span>
                        </NavLink>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 min-w-0">
          {children}
        </main>

      </div>
    </div>
  );
}
