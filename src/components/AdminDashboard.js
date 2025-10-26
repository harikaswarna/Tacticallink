import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  Shield,
  Users,
  MessageSquare,
  AlertTriangle,
  Activity,
  TrendingUp,
  Clock,
  Eye,
  Trash2,
  RefreshCw,
  BarChart3,
  Server,
  Lock,
  Zap
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [threatLogs, setThreatLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get('/admin/dashboard');
      setDashboardData(response.data);
      setThreatLogs(response.data.recent_threats || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getThreatLevelColor = (score) => {
    if (score > 70) return '#ef4444';
    if (score > 40) return '#f59e0b';
    return '#10b981';
  };

  const getThreatLevelText = (score) => {
    if (score > 70) return 'HIGH';
    if (score > 40) return 'MEDIUM';
    return 'LOW';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-military-muted">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-military-text mb-2">
            Failed to load dashboard
          </h3>
          <button onClick={loadDashboardData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-military-dark">
      {/* Header */}
      <div className="bg-military-gray border-b border-military-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-tactical-accent mr-3" />
              <div>
                <h1 className="text-2xl font-bold gradient-text">Admin Dashboard</h1>
                <p className="text-military-muted">TacticalLink Security Monitoring</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={loadDashboardData}
                disabled={refreshing}
                className="btn-secondary flex items-center"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button onClick={logout} className="btn-danger">
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-500 rounded-lg">
                <Users className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-military-muted">Total Users</p>
                <p className="text-2xl font-bold text-military-text">
                  {dashboardData.total_users}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-500 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-military-muted">Active Users</p>
                <p className="text-2xl font-bold text-military-text">
                  {dashboardData.active_users}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-500 rounded-lg">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-military-muted">Messages Today</p>
                <p className="text-2xl font-bold text-military-text">
                  {dashboardData.message_stats?.messages_today || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <div className="p-3 bg-red-500 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-military-muted">Threat Events</p>
                <p className="text-2xl font-bold text-military-text">
                  {threatLogs.length}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Message Activity Chart */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-military-text">Message Activity</h3>
              <BarChart3 className="h-5 w-5 text-military-muted" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={dashboardData.message_stats?.hourly_stats || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="hour" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#161b22',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f0f6fc'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Threat Level Distribution */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-military-text">Threat Level Distribution</h3>
              <PieChart className="h-5 w-5 text-military-muted" />
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Low', value: Object.values(dashboardData.threat_scores || {}).filter(s => s <= 40).length },
                    { name: 'Medium', value: Object.values(dashboardData.threat_scores || {}).filter(s => s > 40 && s <= 70).length },
                    { name: 'High', value: Object.values(dashboardData.threat_scores || {}).filter(s => s > 70).length }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {[0, 1, 2].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#161b22',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f0f6fc'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Threat Logs */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-military-text">Recent Threat Events</h3>
            <div className="flex items-center space-x-2">
              <Server className="h-5 w-5 text-military-muted" />
              <span className="text-sm text-military-muted">Real-time monitoring</span>
            </div>
          </div>

          {threatLogs.length > 0 ? (
            <div className="space-y-4">
              {threatLogs.map((log, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-military-light rounded-lg border border-military-border"
                >
                  <div className="flex items-center space-x-4">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: getThreatLevelColor(log.threat_score) }}
                    ></div>
                    <div>
                      <p className="font-medium text-military-text">
                        User ID: {log.user_id}
                      </p>
                      <p className="text-sm text-military-muted">
                        {log.reason}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getThreatLevelColor(log.threat_score)}`}>
                        {getThreatLevelText(log.threat_score)}
                      </span>
                      <span className="text-sm text-military-muted">
                        {log.threat_score}/100
                      </span>
                    </div>
                    <p className="text-xs text-military-muted">
                      {formatTimestamp(log.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Shield className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <p className="text-military-muted">No threat events detected</p>
            </div>
          )}
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="card p-6">
            <div className="flex items-center">
              <Lock className="h-8 w-8 text-green-400 mr-3" />
              <div>
                <h4 className="font-medium text-military-text">Encryption Status</h4>
                <p className="text-sm text-green-400">AES-256 + RSA-4096 Active</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-blue-400 mr-3" />
              <div>
                <h4 className="font-medium text-military-text">AI Detection</h4>
                <p className="text-sm text-blue-400">Threat Model Online</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-purple-400 mr-3" />
              <div>
                <h4 className="font-medium text-military-text">Self-Destruct</h4>
                <p className="text-sm text-purple-400">Scheduler Running</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
