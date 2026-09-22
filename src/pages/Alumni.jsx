import React from 'react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import PageContainer from '../components/PageContainer';
import { LayoutDashboard, User, Clock, Users, Calendar } from 'lucide-react';

import AlumniDashboardWorkspace from '../modules/alumni/components/AlumniDashboardWorkspace';
import AlumniProfileWorkspace from '../modules/alumni/components/AlumniProfileWorkspace';
import AlumniRequestsWorkspace from '../modules/alumni/components/AlumniRequestsWorkspace';
import AlumniConnectionsWorkspace from '../modules/alumni/components/AlumniConnectionsWorkspace';
import AlumniSessionsWorkspace from '../modules/alumni/components/AlumniSessionsWorkspace';

export default function Alumni() {
  const location = useLocation();

  const tabs = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/alumni/dashboard',
      icon: LayoutDashboard,
    },
    {
      id: 'profile',
      label: 'Mentor Profile',
      path: '/alumni/profile',
      icon: User,
    },
    {
      id: 'requests',
      label: 'Inbound Requests',
      path: '/alumni/requests',
      icon: Clock,
    },
    {
      id: 'connections',
      label: 'Active Mentees',
      path: '/alumni/connections',
      icon: Users,
    },
    {
      id: 'sessions',
      label: 'Sessions Schedule',
      path: '/alumni/sessions',
      icon: Calendar,
    },
  ];

  const activePath =
    location.pathname === '/alumni' || location.pathname === '/alumni/'
      ? '/alumni/dashboard'
      : location.pathname;

  return (
    <PageContainer
      badge="Alumni & Mentor Portal"
      title="Alumni & Mentor Workspace"
      subtitle="Manage your mentor profile, review student mentorship requests, connect 1-on-1 with mentees, and schedule mentorship sessions."
    >
      <div className="space-y-6">
        {/* Navigation Tabs Header */}
        <div className="bg-white rounded-xl p-1.5 shadow-sm border border-slate-200/80 flex flex-wrap gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activePath.startsWith(tab.path);
            return (
              <Link
                key={tab.id}
                to={tab.path}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition ${
                  isActive
                    ? 'bg-purple-700 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Workspace Routes */}
        <Routes>
          <Route path="/" element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AlumniDashboardWorkspace />} />
          <Route path="profile" element={<AlumniProfileWorkspace />} />
          <Route path="requests" element={<AlumniRequestsWorkspace />} />
          <Route path="connections" element={<AlumniConnectionsWorkspace />} />
          <Route path="sessions" element={<AlumniSessionsWorkspace />} />
        </Routes>
      </div>
    </PageContainer>
  );
}
