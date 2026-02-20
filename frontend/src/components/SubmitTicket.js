import React, { useState } from 'react';
import { ticketAPI } from '../api';

const CATEGORIES = ['billing', 'technical', 'account', 'general'];
const PRIORITIES = ['low', 'medium', 'high', 'critical'];

function SubmitTicket({ onTicketCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: '',
  });
  const [isClassifying, setIsClassifying] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleDescriptionChange = async (e) => {
    const description = e.target.value;
    setFormData({ ...formData, description });

    // Auto-classify when description has sufficient content
    if (description.trim().length > 10) {
      setIsClassifying(true);
      try {
        const response = await ticketAPI.classifyTicket(description);
        setFormData((prev) => ({
          ...prev,
          category: response.data.suggested_category,
          priority: response.data.suggested_priority,
        }));
      } catch (err) {
        console.error('Classification failed:', err);
        // Silently fail - user can still select manually
      } finally {
        setIsClassifying(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!formData.title.trim() || !formData.description.trim() || 
        !formData.category || !formData.priority) {
      setError('All fields are required');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await ticketAPI.createTicket(formData);
      setSuccess(true);
      // Clear form
      setFormData({
        title: '',
        description: '',
        category: '',
        priority: '',
      });
      // Notify parent component
      if (onTicketCreated) {
        onTicketCreated(response.data);
      }
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create ticket');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="submit-ticket">
      <h2>Submit a Support Ticket</h2>
      
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">Ticket created successfully!</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            maxLength="200"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Brief description of your issue"
            disabled={isSubmitting}
          />
          <small>{formData.title.length}/200</small>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            rows="5"
            value={formData.description}
            onChange={handleDescriptionChange}
            placeholder="Detailed description of your issue..."
            disabled={isSubmitting}
          />
          {isClassifying && (
            <small className="classifying">🤖 AI is analyzing your description...</small>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              disabled={isSubmitting}
            >
              <option value="">Select category...</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="priority">Priority *</label>
            <select
              id="priority"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              disabled={isSubmitting}
            >
              <option value="">Select priority...</option>
              {PRIORITIES.map((pri) => (
                <option key={pri} value={pri}>
                  {pri.charAt(0).toUpperCase() + pri.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="submit" disabled={isSubmitting || isClassifying}>
          {isSubmitting ? 'Submitting...' : 'Submit Ticket'}
        </button>
      </form>
    </div>
  );
}

export default SubmitTicket;
