import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          // Verify token by making a request to a protected endpoint
          const response = await axios.get('/auth/verify');
          if (response.data && response.data.user_id) {
            setUser({
              id: response.data.user_id,
              username: response.data.username,
              is_admin: response.data.is_admin,
              token: token
            });
          } else {
            // Token exists but verification failed
            console.error('Token verification failed: Invalid response');
            logout();
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Only logout if it's not a network error
          if (error.response && error.response.status === 401) {
            logout();
          } else {
            // For network errors, keep the token but don't set user
            console.warn('Network error during token verification, keeping token');
            setLoading(false);
            return;
          }
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post('/auth/login', {
        username,
        password
      });

      const { access_token, user_id, username: userUsername, public_key } = response.data;
      
      // Store token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Set user data immediately
      const userData = {
        id: user_id,
        username: userUsername,
        public_key,
        token: access_token
      };
      setUser(userData);
      
      // Set axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success('Login successful');
      return { success: true, user: userData };
      
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/auth/register', {
        username,
        email,
        password
      });

      const { access_token, user_id, public_key } = response.data;
      
      // Store token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Set user data
      const userData = {
        id: user_id,
        username,
        public_key,
        token: access_token
      };
      setUser(userData);
      
      // Set axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success('Registration successful');
      return { success: true, user: userData };
      
    } catch (error) {
      const message = error.response?.data?.error || 'Registration failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
