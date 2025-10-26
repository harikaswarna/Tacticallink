import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../contexts/SocketContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  Send,
  Shield,
  Clock,
  Eye,
  EyeOff,
  Settings,
  Users,
  AlertTriangle,
  Lock,
  Timer,
  Trash2,
  Plus,
  Search,
  RefreshCw,
  MessageSquare
} from 'lucide-react';

const Chat = () => {
  const { user, logout } = useAuth();
  const { connected, threatLevel } = useSocket();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [selfDestructTime, setSelfDestructTime] = useState(0);
  const [readOnce, setReadOnce] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(false);

  // Load users and messages on component mount
  useEffect(() => {
    if (user) {
      loadUsers();
      loadMessages();
    }
  }, [user]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Poll for new messages every 3 seconds when a user is selected
  useEffect(() => {
    if (!selectedUser) return;
    
    const interval = setInterval(() => {
      loadMessages();
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedUser]);

  // Poll for users every 15 seconds
  useEffect(() => {
    if (!user) return;
    
    const interval = setInterval(() => {
      loadUsers();
    }, 15000);

    return () => clearInterval(interval);
  }, [user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadUsers = async () => {
    try {
      const response = await axios.get('/chat/users');
      setUsers(response.data.users);
      console.log('Loaded users:', response.data.users.length);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Failed to load users');
    }
  };

  const loadMessages = async () => {
    try {
      if (selectedUser) {
        // Load conversation messages
        const response = await axios.get(`/chat/conversation/${selectedUser._id}`);
        setMessages(response.data.messages);
        console.log('Loaded conversation messages:', response.data.messages.length);
      } else {
        // Load pending messages when no user is selected
        const response = await axios.get('/chat/receive');
        setMessages(response.data.messages);
        console.log('Loaded pending messages:', response.data.messages.length);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      // Don't show toast for every polling error, just log it
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
      }
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedUser) return;

    setLoading(true);
    try {
      const response = await axios.post('/chat/send', {
        recipient_id: selectedUser._id,
        message: newMessage,
        self_destruct_time: selfDestructTime,
        read_once: readOnce
      });

      if (response.data.threat_score > 70) {
        toast.error(`High threat level detected: ${response.data.threat_score}`);
      }

      setNewMessage('');
      setSelfDestructTime(0);
      setReadOnce(false);
      
      // Reload messages to show the sent message
      setTimeout(() => {
        loadMessages();
      }, 500);
      
      toast.success('Message sent securely');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const deleteMessage = async (messageId) => {
    try {
      await axios.delete(`/delete/message/${messageId}`);
      setMessages(messages.filter(m => m.id !== messageId));
      toast.success('Message deleted');
    } catch (error) {
      toast.error('Failed to delete message');
    }
  };

  const getThreatLevelColor = (level) => {
    if (level > 70) return 'text-red-400';
    if (level > 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getThreatLevelText = (level) => {
    if (level > 70) return 'HIGH';
    if (level > 40) return 'MEDIUM';
    return 'LOW';
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-screen flex bg-military-dark">
      {/* Sidebar */}
      <div className="w-80 bg-military-gray border-r border-military-border flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-military-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-tactical-accent mr-2" />
              <h1 className="text-xl font-bold gradient-text">TacticalLink</h1>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-military-light rounded-lg transition-colors"
            >
              <Settings className="h-5 w-5 text-military-muted" />
            </button>
            <button
              onClick={() => navigate('/group-chat')}
              className="p-2 hover:bg-military-light rounded-lg transition-colors"
              title="Group Chat"
            >
              <MessageSquare className="h-5 w-5 text-military-muted" />
            </button>
          </div>

          {/* Connection Status */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center">
              <div className={`w-2 h-2 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-military-muted">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex items-center">
              <AlertTriangle className="h-4 w-4 mr-1" />
              <span className={getThreatLevelColor(threatLevel)}>
                {getThreatLevelText(threatLevel)}
              </span>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="p-4 border-b border-military-border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-tactical-accent rounded-full flex items-center justify-center mr-3">
              <span className="text-white font-medium">
                {user.username.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <p className="font-medium text-military-text">{user.username}</p>
              <p className="text-xs text-military-muted">Online</p>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-military-border">
          <div className="flex space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-military-muted" />
              <input
                type="text"
                placeholder="Search users..."
                className="input-field pl-10 w-full text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={loadUsers}
              className="btn-secondary px-3 py-2"
              title="Refresh users"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Users List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <h3 className="text-sm font-medium text-military-muted mb-2 px-2">
              Active Users ({filteredUsers.length})
            </h3>
            {filteredUsers.length > 0 ? (
              filteredUsers.map((user) => (
                <button
                  key={user._id}
                  onClick={() => setSelectedUser(user)}
                  className={`w-full flex items-center p-3 rounded-lg mb-1 transition-colors ${
                    selectedUser?._id === user._id
                      ? 'bg-tactical-accent text-white'
                      : 'hover:bg-military-light text-military-text'
                  }`}
                >
                  <div className="w-8 h-8 bg-military-light rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-medium">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 text-left">
                    <p className="font-medium">{user.username}</p>
                    <p className="text-xs opacity-75">
                      {user.is_admin ? 'Admin' : 'User'}
                    </p>
                  </div>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </button>
              ))
            ) : (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-military-muted mx-auto mb-4" />
                <p className="text-military-muted text-sm">
                  {searchTerm ? 'No users found matching your search' : 'No other users available'}
                </p>
                {!searchTerm && (
                  <p className="text-military-muted text-xs mt-2">
                    Create another account to start chatting
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Logout */}
        <div className="p-4 border-t border-military-border">
          <button
            onClick={logout}
            className="btn-danger w-full"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedUser ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-military-border bg-military-gray">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-military-light rounded-full flex items-center justify-center mr-3">
                    <span className="text-military-text font-medium">
                      {selectedUser.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h2 className="font-medium text-military-text">{selectedUser.username}</h2>
                    <p className="text-sm text-military-muted">End-to-end encrypted</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Lock className="h-4 w-4 text-green-400" />
                  <span className="text-xs text-green-400">Encrypted</span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`message-bubble ${
                        message.sender_id === user.id ? 'message-sent' : 'message-received'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs opacity-75">
                          {formatTime(message.timestamp)}
                        </span>
                        <div className="flex items-center space-x-2">
                          {message.read_once && (
                            <div className="flex items-center text-xs opacity-75">
                              <Eye className="h-3 w-3 mr-1" />
                              Read once
                            </div>
                          )}
                          {message.is_read && message.sender_id === user.id && (
                            <div className="flex items-center text-xs opacity-75">
                              <Eye className="h-3 w-3 mr-1" />
                              Read
                            </div>
                          )}
                          {message.sender_id === user.id && (
                            <button
                              onClick={() => deleteMessage(message.id)}
                              className="hover:text-red-400 transition-colors"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-military-border bg-military-gray">
              <form onSubmit={sendMessage} className="space-y-3">
                {/* Self-destruct settings */}
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center">
                    <Timer className="h-4 w-4 mr-1 text-military-muted" />
                    <select
                      value={selfDestructTime}
                      onChange={(e) => setSelfDestructTime(parseInt(e.target.value))}
                      className="input-field text-sm"
                    >
                      <option value={0}>No self-destruct</option>
                      <option value={60}>1 minute</option>
                      <option value={300}>5 minutes</option>
                      <option value={600}>10 minutes</option>
                      <option value={3600}>1 hour</option>
                    </select>
                  </div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={readOnce}
                      onChange={(e) => setReadOnce(e.target.checked)}
                      className="mr-2"
                    />
                    <Eye className="h-4 w-4 mr-1" />
                    Read once
                  </label>
                </div>

                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your secure message..."
                    className="input-field flex-1"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !newMessage.trim()}
                    className="btn-primary px-4 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <div className="loading-spinner"></div>
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Shield className="h-16 w-16 text-military-muted mx-auto mb-4" />
              <h3 className="text-lg font-medium text-military-text mb-2">
                Select a user to start chatting
              </h3>
              <p className="text-military-muted">
                Choose from the list on the left to begin a secure conversation
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
