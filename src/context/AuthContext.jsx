import React, { createContext, useState, useEffect, useCallback } from 'react';
import api from '../lib/api';

export const AuthContext = createContext(null);

export const TOKEN_STORAGE_KEY = 'skilly_auth_token';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Verify and fetch current user profile on initial load or token change
  const loadCurrentUser = useCallback(async (authToken) => {
    if (!authToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      setUser(response.data);
      setAuthError(null);
    } catch (err) {
      console.warn('Session verification failed or token expired:', err?.response?.data?.detail || err.message);
      // Remove stale/expired token
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedToken) {
      loadCurrentUser(storedToken);
    } else {
      setLoading(false);
    }
  }, [loadCurrentUser]);

  // Login handler
  const login = async ({ email, password }) => {
    try {
      setAuthError(null);
      const response = await api.post('/auth/login', {
        email: email.trim().toLowerCase(),
        password,
      });

      const { access_token, user: userData } = response.data;
      localStorage.setItem(TOKEN_STORAGE_KEY, access_token);
      setToken(access_token);
      setUser(userData);
      return { success: true, user: userData };
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Authentication failed. Please check your credentials.';
      setAuthError(message);
      return { success: false, error: message };
    }
  };

  // Registration handler
  const register = async (registrationData) => {
    try {
      setAuthError(null);
      const response = await api.post('/auth/register', {
        email: registrationData.email.trim().toLowerCase(),
        password: registrationData.password,
        role: registrationData.role,
        fullName: registrationData.fullName,
        first_name: registrationData.first_name,
        last_name: registrationData.last_name,
      });

      // Auto-login after successful registration
      const loginResult = await login({
        email: registrationData.email,
        password: registrationData.password,
      });

      return loginResult.success
        ? loginResult
        : { success: true, user: response.data, requiresManualLogin: true };
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Registration failed. Please verify your details.';
      setAuthError(message);
      return { success: false, error: message };
    }
  };

  // Logout handler
  const logout = async () => {
    try {
      if (token) {
        await api.post('/auth/logout').catch(() => {});
      }
    } finally {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setToken(null);
      setUser(null);
      setAuthError(null);
    }
  };

  const value = {
    user,
    token,
    loading,
    authError,
    isAuthenticated: Boolean(token && user),
    login,
    register,
    logout,
    refreshUser: () => loadCurrentUser(token),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
