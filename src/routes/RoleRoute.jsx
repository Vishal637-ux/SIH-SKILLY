import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';

// Map canonical database roles to their designated home path
const ROLE_HOME_PATHS = {
  STUDENT: '/student',
  COLLEGE_ADMIN: '/college',
  TEACHER: '/teacher',
  INDUSTRY: '/industry',
  ALUMNI: '/alumni',
};

export default function RoleRoute({ allowedRoles = [], children }) {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-10rem)] flex items-center justify-center">
        <Loading message="Checking role authorization..." />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = (user.role || '').toUpperCase();
  const normalizedAllowed = allowedRoles.map((r) => r.toUpperCase());

  const hasAccess = normalizedAllowed.includes(userRole);

  if (!hasAccess) {
    // Redirect unauthorized users to their designated portal
    const targetPath = ROLE_HOME_PATHS[userRole] || '/';
    return <Navigate to={targetPath} replace />;
  }

  return children ? children : <Outlet />;
}
