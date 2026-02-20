import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Ticket API calls
export const ticketAPI = {
  // Get all tickets with optional filters
  getTickets: (params = {}) => {
    return api.get('/tickets/', { params });
  },

  // Create a new ticket
  createTicket: (data) => {
    return api.post('/tickets/', data);
  },

  // Update a ticket
  updateTicket: (id, data) => {
    return api.patch(`/tickets/${id}/`, data);
  },

  // Get ticket statistics
  getStats: () => {
    return api.get('/tickets/stats/');
  },

  // Classify ticket description
  classifyTicket: (description) => {
    return api.post('/tickets/classify/', { description });
  },
};

export default api;
