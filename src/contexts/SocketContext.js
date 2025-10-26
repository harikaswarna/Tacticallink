import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [connected, setConnected] = useState(false);
  const [threatLevel, setThreatLevel] = useState(0);
  const { user } = useAuth();

  useEffect(() => {
    if (user && user.token) {
      // Start polling for status updates instead of WebSocket
      const pollStatus = async () => {
        try {
          const response = await axios.get('/ws/status');
          if (response.data) {
            setConnected(true);
            setThreatLevel(response.data.threat_score || 0);
          }
        } catch (error) {
          console.error('Status polling error:', error);
          setConnected(false);
        }
      };

      // Initial status check
      pollStatus();

      // Poll every 5 seconds
      const interval = setInterval(pollStatus, 5000);

      return () => {
        clearInterval(interval);
        setConnected(false);
      };
    }
  }, [user]);

  const value = {
    connected,
    threatLevel
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
