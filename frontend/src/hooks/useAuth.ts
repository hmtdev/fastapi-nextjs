'use client';

import { useState, useEffect, useCallback } from 'react';
import nextApiClient from '@/lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  avatar_url: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    try {
      const response = await nextApiClient.get('/me');
      setUser(response.data.data);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
      setIsLoggedIn(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const logout = async () => {
    try {
      await nextApiClient.post('/logout');
      setUser(null);
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const refresh = useCallback(() => {
    return fetchUser();
  }, [fetchUser]);

  return {
    user,
    loading,
    isLoggedIn,
    logout,
    refresh
  };
}