import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../contexts/SocketContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  Send,
  Shield,
  Users,
  Plus,
  Search,
  RefreshCw,
  MessageSquare,
  Settings,
  LogOut,
  AlertTriangle,
  Lock,
  User
} from 'lucide-react';

const GroupChat = () => {
  const { user, logout } = useAuth();
  const { connected, threatLevel } = useSocket();
  const navigate = useNavigate();
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomDescription, setNewRoomDescription] = useState('');
  const [isPrivateRoom, setIsPrivateRoom] = useState(false);
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [showJoinByKey, setShowJoinByKey] = useState(false);
  const [joinKey, setJoinKey] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(false);

  // Load rooms and messages on component mount
  useEffect(() => {
    if (user) {
      loadRooms();
    }
  }, [user]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Poll for new messages every 3 seconds when a room is selected
  useEffect(() => {
    if (!selectedRoom) return;
    
    const interval = setInterval(() => {
      loadMessages();
    }, 3000);

    return () => clearInterval(interval);
  }, [selectedRoom]);

  // Poll for rooms every 15 seconds
  useEffect(() => {
    if (!user) return;
    
    const interval = setInterval(() => {
      loadRooms();
    }, 15000);

    return () => clearInterval(interval);
  }, [user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadRooms = async () => {
    try {
      const response = await axios.get('/chat/rooms');
      setRooms(response.data.rooms);
      console.log('Loaded rooms:', response.data.rooms.length);
    } catch (error) {
      console.error('Error loading rooms:', error);
      toast.error('Failed to load chat rooms');
    }
  };

  const loadMessages = async () => {
    try {
      if (selectedRoom) {
        const response = await axios.get(`/chat/rooms/${selectedRoom._id}/messages`);
        setMessages(response.data.messages.reverse()); // Reverse to show oldest first
        console.log('Loaded room messages:', response.data.messages.length);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
      }
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedRoom) return;

    setLoading(true);
    try {
      const response = await axios.post(`/chat/rooms/${selectedRoom._id}/messages`, {
        message: newMessage,
        message_type: 'text'
      });

      if (response.data.threat_score > 70) {
        toast.error(`High threat level detected: ${response.data.threat_score}`);
      }

      setNewMessage('');
      
      // Reload messages to show the sent message
      setTimeout(() => {
        loadMessages();
      }, 500);
      
      toast.success('Message sent');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const createRoom = async (e) => {
    e.preventDefault();
    if (!newRoomName.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('/chat/rooms', {
        name: newRoomName,
        description: newRoomDescription,
        is_public: !isPrivateRoom,
        max_members: 50
      });

      setNewRoomName('');
      setNewRoomDescription('');
      setIsPrivateRoom(false);
      setShowCreateRoom(false);
      loadRooms();
      
      if (!isPrivateRoom) {
        toast.success('Chat room created successfully');
      } else {
        toast.success(`Private room created! Share this key: ${response.data.join_key}`);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create room');
    } finally {
      setLoading(false);
    }
  };

  const joinRoom = async (room) => {
    try {
      await axios.post(`/chat/rooms/${room._id}/join`);
      setSelectedRoom(room);
      loadMessages();
      toast.success(`Joined ${room.name}`);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to join room');
    }
  };

  const joinRoomByKey = async (e) => {
    e.preventDefault();
    if (!joinKey.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('/chat/rooms/join-by-key', {
        join_key: joinKey
      });

      setJoinKey('');
      setShowJoinByKey(false);
      loadRooms();
      toast.success(`Successfully joined ${response.data.room_name}`);
      
      // Auto-select the joined room
      const joinedRoom = rooms ? rooms.find(room => room._id === response.data.room_id) : null;
      if (joinedRoom) {
        setSelectedRoom(joinedRoom);
      } else {
        // Create a temporary room object if not found in current rooms list
        setSelectedRoom({ 
          _id: response.data.room_id, 
          name: response.data.room_name 
        });
      }
      loadMessages();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to join room');
    } finally {
      setLoading(false);
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

  const filteredRooms = rooms ? rooms.filter(room =>
    room.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

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
              onClick={() => setShowCreateRoom(!showCreateRoom)}
              className="p-2 hover:bg-military-light rounded-lg transition-colors"
              title="Create Room"
            >
              <Plus className="h-5 w-5 text-military-muted" />
            </button>
            <button
              onClick={() => setShowJoinByKey(!showJoinByKey)}
              className="p-2 hover:bg-military-light rounded-lg transition-colors"
              title="Join by Key"
            >
              <Lock className="h-5 w-5 text-military-muted" />
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="p-2 hover:bg-military-light rounded-lg transition-colors"
              title="Private Chat"
            >
              <User className="h-5 w-5 text-military-muted" />
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

        {/* Create Room Form */}
        {showCreateRoom && (
          <div className="p-4 border-b border-military-border bg-military-light">
            <h3 className="text-sm font-medium text-military-text mb-3">Create New Room</h3>
            <form onSubmit={createRoom} className="space-y-3">
              <input
                type="text"
                placeholder="Room name"
                className="input-field w-full text-sm"
                value={newRoomName}
                onChange={(e) => setNewRoomName(e.target.value)}
                disabled={loading}
              />
              <input
                type="text"
                placeholder="Description (optional)"
                className="input-field w-full text-sm"
                value={newRoomDescription}
                onChange={(e) => setNewRoomDescription(e.target.value)}
                disabled={loading}
              />
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="privateRoom"
                  checked={isPrivateRoom}
                  onChange={(e) => setIsPrivateRoom(e.target.checked)}
                  className="rounded border-military-border"
                  disabled={loading}
                />
                <label htmlFor="privateRoom" className="text-sm text-military-text">
                  Private room (requires join key)
                </label>
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={loading || !newRoomName.trim()}
                  className="btn-primary flex-1 text-sm disabled:opacity-50"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateRoom(false)}
                  className="btn-secondary text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Join by Key Form */}
        {showJoinByKey && (
          <div className="p-4 border-b border-military-border bg-military-light">
            <h3 className="text-sm font-medium text-military-text mb-3">Join Room by Key</h3>
            <form onSubmit={joinRoomByKey} className="space-y-3">
              <input
                type="text"
                placeholder="Enter join key"
                className="input-field w-full text-sm"
                value={joinKey}
                onChange={(e) => setJoinKey(e.target.value.toUpperCase())}
                disabled={loading}
                maxLength={8}
              />
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={loading || !joinKey.trim()}
                  className="btn-primary flex-1 text-sm disabled:opacity-50"
                >
                  Join Room
                </button>
                <button
                  type="button"
                  onClick={() => setShowJoinByKey(false)}
                  className="btn-secondary text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Search */}
        <div className="p-4 border-b border-military-border">
          <div className="flex space-x-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-military-muted" />
              <input
                type="text"
                placeholder="Search rooms..."
                className="input-field pl-10 w-full text-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={loadRooms}
              className="btn-secondary px-3 py-2"
              title="Refresh rooms"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Rooms List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2">
            <h3 className="text-sm font-medium text-military-muted mb-2 px-2">
              Chat Rooms ({filteredRooms.length})
            </h3>
            {filteredRooms.length > 0 ? (
              filteredRooms.map((room) => (
                <button
                  key={room._id}
                  onClick={() => joinRoom(room)}
                  className={`w-full flex items-center p-3 rounded-lg mb-1 transition-colors ${
                    selectedRoom?._id === room._id
                      ? 'bg-tactical-accent text-white'
                      : 'hover:bg-military-light text-military-text'
                  }`}
                >
                  <div className="w-8 h-8 bg-military-light rounded-full flex items-center justify-center mr-3">
                    <MessageSquare className="h-4 w-4" />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="font-medium">{room.name}</p>
                    <p className="text-xs opacity-75">
                      {room.members ? room.members.length : 0} members
                    </p>
                  </div>
                  <div className="flex items-center space-x-1">
                    {room.is_public ? (
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    ) : (
                      <Lock className="h-3 w-3" />
                    )}
                  </div>
                </button>
              ))
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-military-muted mx-auto mb-4" />
                <p className="text-military-muted text-sm">
                  {searchTerm ? 'No rooms found matching your search' : 'No chat rooms available'}
                </p>
                {!searchTerm && (
                  <p className="text-military-muted text-xs mt-2">
                    Create a room to start chatting
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
        {selectedRoom ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-military-border bg-military-gray">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-military-light rounded-full flex items-center justify-center mr-3">
                    <MessageSquare className="h-5 w-5 text-military-text" />
                  </div>
                  <div>
                    <h2 className="font-medium text-military-text">{selectedRoom.name}</h2>
                    <p className="text-sm text-military-muted">
                      {selectedRoom.members.length} members • {selectedRoom.description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-military-muted" />
                  <span className="text-xs text-military-muted">
                    {selectedRoom.members.length} online
                  </span>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message._id}
                  className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`message-bubble ${
                      message.sender_id === user.id ? 'message-sent' : 'message-received'
                    }`}
                  >
                    {message.sender_id !== user.id && (
                      <p className="text-xs font-medium opacity-75 mb-1">
                        {message.sender_username}
                      </p>
                    )}
                    <p className="text-sm">{message.content}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs opacity-75">
                        {formatTime(message.timestamp)}
                      </span>
                      {message.sender_id === user.id && (
                        <button
                          onClick={() => {
                            // TODO: Implement delete message
                            console.log('Delete message:', message._id);
                          }}
                          className="hover:text-red-400 transition-colors ml-2"
                        >
                          <Settings className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-military-border bg-military-gray">
              <form onSubmit={sendMessage} className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type your message..."
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
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageSquare className="h-16 w-16 text-military-muted mx-auto mb-4" />
              <h3 className="text-lg font-medium text-military-text mb-2">
                Select a chat room to start messaging
              </h3>
              <p className="text-military-muted">
                Choose from the list on the left or create a new room
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupChat;
