import React, { useState, useEffect } from 'react';
import { ticketAPI } from '../api';

function StatsDashboard({ refreshTrigger }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  const fetchStats = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await ticketAPI.getStats();
      setStats(response.data);
    } catch (err) {
      setError('Failed to load statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="stats-dashboard loading">Loading statistics...</div>;
  }

  if (error) {
    return <div className="stats-dashboard alert alert-error">{error}</div>;
  }

  return (
    <div className="stats-dashboard">
      <h2>Ticket Statistics</h2>

      {/* Summary Cards */}
      <div className="stats-summary">
        <div className="stat-card">
          <h3>Total Tickets</h3>
          <div className="stat-value">{stats.total_tickets}</div>
        </div>

        <div className="stat-card">
          <h3>Open Tickets</h3>
          <div className="stat-value">{stats.open_tickets}</div>
        </div>

        <div className="stat-card">
          <h3>Avg. per Day</h3>
          <div className="stat-value">{stats.avg_tickets_per_day}</div>
        </div>
      </div>

      {/* Priority Breakdown */}
      <div className="stats-breakdown">
        <h3>Priority Breakdown</h3>
        <div className="breakdown-items">
          {Object.entries(stats.priority_breakdown || {}).map(([priority, count]) => (
            <div key={priority} className={`breakdown-item priority-${priority}`}>
              <span className="breakdown-label">
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </span>
              <span className="breakdown-value">{count}</span>
            </div>
          ))}
          {Object.keys(stats.priority_breakdown || {}).length === 0 && (
            <div className="no-data">No data available</div>
          )}
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="stats-breakdown">
        <h3>Category Breakdown</h3>
        <div className="breakdown-items">
          {Object.entries(stats.category_breakdown || {}).map(([category, count]) => (
            <div key={category} className="breakdown-item">
              <span className="breakdown-label">
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </span>
              <span className="breakdown-value">{count}</span>
            </div>
          ))}
          {Object.keys(stats.category_breakdown || {}).length === 0 && (
            <div className="no-data">No data available</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StatsDashboard;
