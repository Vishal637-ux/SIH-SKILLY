import React from 'react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import PageContainer from '../components/PageContainer';
import { LayoutDashboard, Building2, Briefcase, Users, Award, Calendar, BarChart3 } from 'lucide-react';

import IndustryDashboardWorkspace from '../modules/industry/components/IndustryDashboardWorkspace';
import IndustryProfileWorkspace from '../modules/industry/components/IndustryProfileWorkspace';
import IndustryOpportunitiesWorkspace from '../modules/industry/components/IndustryOpportunitiesWorkspace';
import IndustryApplicationsWorkspace from '../modules/industry/components/IndustryApplicationsWorkspace';
import IndustryInternshipsWorkspace from '../modules/industry/components/IndustryInternshipsWorkspace';
import IndustryInteractionsWorkspace from '../modules/industry/components/IndustryInteractionsWorkspace';
import IndustryAnalyticsWorkspace from '../modules/industry/components/IndustryAnalyticsWorkspace';

export default function Industry() {
  const location = useLocation();

  const tabs = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/industry/dashboard',
      icon: LayoutDashboard,
    },
    {
      id: 'profile',
      label: 'Corporate Profile',
      path: '/industry/profile',
      icon: Building2,
    },
    {
      id: 'opportunities',
      label: 'Opportunities',
      path: '/industry/opportunities',
      icon: Briefcase,
    },
    {
      id: 'applications',
      label: 'ATS Applications',
      path: '/industry/applications',
      icon: Users,
    },
    {
      id: 'internships',
      label: 'Internships',
      path: '/industry/internships',
      icon: Award,
    },
    {
      id: 'interactions',
      label: 'Interactions',
      path: '/industry/interactions',
      icon: Calendar,
    },
    {
      id: 'analytics',
      label: 'Hiring Analytics',
      path: '/industry/analytics',
      icon: BarChart3,
    },
  ];

  const activePath =
    location.pathname === '/industry' || location.pathname === '/industry/'
      ? '/industry/dashboard'
      : location.pathname;

  return (
    <PageContainer
      badge="Industry & Corporate Portal"
      title="Industry & Recruiter Workspace"
      subtitle="Job postings, skill-matrix candidate shortlisting, ATS state management, internship supervision, and campus recruitment interactions."
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
                    ? 'bg-blue-700 text-white shadow-sm'
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
          <Route path="dashboard" element={<IndustryDashboardWorkspace />} />
          <Route path="profile" element={<IndustryProfileWorkspace />} />
          <Route path="opportunities" element={<IndustryOpportunitiesWorkspace />} />
          <Route path="applications" element={<IndustryApplicationsWorkspace />} />
          <Route path="internships" element={<IndustryInternshipsWorkspace />} />
          <Route path="interactions" element={<IndustryInteractionsWorkspace />} />
          <Route path="analytics" element={<IndustryAnalyticsWorkspace />} />
        </Routes>
      </div>
    </PageContainer>
  );
}
