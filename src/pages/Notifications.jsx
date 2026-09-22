import React from 'react';
import PageContainer from '../components/PageContainer';
import NotificationCenter from '../components/NotificationCenter';
import useAuth from '../hooks/useAuth';

export default function Notifications() {
  const { user } = useAuth();
  return (
    <PageContainer
      badge="Platform Module"
      title="Notifications & Alerts"
      subtitle="Stay updated on mentorship requests, application status changes, community interactions, and platform milestones."
    >
      <NotificationCenter userRole={user?.role || 'STUDENT'} />
    </PageContainer>
  );
}
