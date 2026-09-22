import React from 'react';
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import PageContainer from '../components/PageContainer';
import { LayoutDashboard, User, Users, BookOpen, UserCheck, Calendar, BarChart3 } from 'lucide-react';

import TeacherDashboardWorkspace from '../modules/teacher/components/TeacherDashboardWorkspace';
import TeacherProfileWorkspace from '../modules/teacher/components/TeacherProfileWorkspace';
import TeacherStudentRosterWorkspace from '../modules/teacher/components/TeacherStudentRosterWorkspace';
import TeacherTrainingWorkspace from '../modules/teacher/components/TeacherTrainingWorkspace';
import TeacherMentorshipWorkspace from '../modules/teacher/components/TeacherMentorshipWorkspace';
import TeacherActivityWorkspace from '../modules/teacher/components/TeacherActivityWorkspace';
import TeacherAnalyticsWorkspace from '../modules/teacher/components/TeacherAnalyticsWorkspace';

export default function Teacher() {
  const location = useLocation();

  const tabs = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/teacher/dashboard',
      icon: LayoutDashboard
    },
    {
      id: 'profile',
      label: 'Academic Identity',
      path: '/teacher/profile',
      icon: User
    },
    {
      id: 'students',
      label: 'Student Roster',
      path: '/teacher/students',
      icon: Users
    },
    {
      id: 'training',
      label: 'Training & Workshops',
      path: '/teacher/training',
      icon: BookOpen
    },
    {
      id: 'mentorship',
      label: 'Mentorship',
      path: '/teacher/mentorship',
      icon: UserCheck
    },
    {
      id: 'activities',
      label: 'Activities',
      path: '/teacher/activities',
      icon: Calendar
    },
    {
      id: 'analytics',
      label: 'Analytics',
      path: '/teacher/analytics',
      icon: BarChart3
    }
  ];

  const activePath = location.pathname === '/teacher' || location.pathname === '/teacher/'
    ? '/teacher/dashboard'
    : location.pathname;

  return (
    <PageContainer
      badge="Faculty Portal"
      title="Teacher & Academician Portal"
      subtitle="Academic department monitoring, workshops, student mentorship, campus guest lectures, and department skill analytics."
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
                    ? 'bg-emerald-600 text-white shadow-sm'
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
          <Route path="dashboard" element={<TeacherDashboardWorkspace />} />
          <Route path="profile" element={<TeacherProfileWorkspace />} />
          <Route path="students" element={<TeacherStudentRosterWorkspace />} />
          <Route path="training" element={<TeacherTrainingWorkspace />} />
          <Route path="mentorship" element={<TeacherMentorshipWorkspace />} />
          <Route path="activities" element={<TeacherActivityWorkspace />} />
          <Route path="analytics" element={<TeacherAnalyticsWorkspace />} />
        </Routes>
      </div>
    </PageContainer>
  );
}
