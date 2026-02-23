import React, { useState, useEffect, useCallback } from 'react';
import { ticketAPI } from '../api';

const CATEGORIES = ['', 'billing', 'technical', 'account', 'general'];
const PRIORITIES = ['', 'low', 'medium', 'high', 'critical'];
const STATUSES = ['', 'open', 'in_progress', 'resolved', 'closed'];

function TicketList({ refreshTrigger }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    priority: '',
    status: '',
    search: '',
  });
  const [editingTicket, setEditingTicket] = useState(null);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = {};
      if (filters.category) params.category = filters.category;
      if (filters.priority) params.priority = filters.priority;
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;

      const response = await ticketAPI.getTickets(params);
      setTickets(response.data);
    } catch (err) {
      setError('Failed to load tickets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets, refreshTrigger]);

  const handleStatusUpdate = async (ticketId, newStatus) => {
    try {
      await ticketAPI.updateTicket(ticketId, { status: newStatus });
      setEditingTicket(null);
      fetchTickets(); // Refresh list
    } catch (err) {
      alert('Failed to update ticket status');
      console.error(err);
    }
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getPriorityClass = (priority) => {
    return `priority-${priority}`;
  };

  const getStatusClass = (status) => {
    return `status-${status.replace('_', '-')}`;
  };

  return (
    <div className="ticket-list">
      <h2>Support Tickets</h2>

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search tickets..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />

        <select
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
        >
          <option value="">All Categories</option>
          {CATEGORIES.slice(1).map((cat) => (
            <option key={cat} value={cat}>
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={filters.priority}
          onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
        >
          <option value="">All Priorities</option>
          {PRIORITIES.slice(1).map((pri) => (
            <option key={pri} value={pri}>
              {pri.charAt(0).toUpperCase() + pri.slice(1)}
            </option>
          ))}
        </select>

        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        >
          <option value="">All Statuses</option>
          {STATUSES.slice(1).map((stat) => (
            <option key={stat} value={stat}>
              {stat.replace('_', ' ').charAt(0).toUpperCase() + stat.slice(1).replace('_', ' ')}
            </option>
          ))}
        </select>
      </div>

      {/* Loading/Error states */}
      {loading && <div className="loading">Loading tickets...</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Tickets */}
      {!loading && tickets.length === 0 && (
        <div className="no-tickets">No tickets found</div>
      )}

      {!loading && tickets.length > 0 && (
        <div className="tickets">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="ticket-card">
              <div className="ticket-header">
                <h3>{ticket.title}</h3>
                <span className={`badge ${getPriorityClass(ticket.priority)}`}>
                  {ticket.priority}
                </span>
              </div>

              <p className="ticket-description">{truncateText(ticket.description)}</p>

              <div className="ticket-meta">
                <span className="category">
                  Category: {ticket.category.charAt(0).toUpperCase() + ticket.category.slice(1)}
                </span>
                <span className={`status ${getStatusClass(ticket.status)}`}>
                  {ticket.status.replace('_', ' ').toUpperCase()}
                </span>
                <span className="date">Created: {formatDate(ticket.created_at)}</span>
              </div>

              {/* Status Update */}
              <div className="ticket-actions">
                {editingTicket === ticket.id ? (
                  <>
                    <select
                      defaultValue={ticket.status}
                      onChange={(e) => handleStatusUpdate(ticket.id, e.target.value)}
                    >
                      {STATUSES.slice(1).map((stat) => (
                        <option key={stat} value={stat}>
                          {stat.replace('_', ' ').charAt(0).toUpperCase() + stat.slice(1).replace('_', ' ')}
                        </option>
                      ))}
                    </select>
                    <button onClick={() => setEditingTicket(null)}>Cancel</button>
                  </>
                ) : (
                  <button onClick={() => setEditingTicket(ticket.id)}>
                    Update Status
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TicketList;
