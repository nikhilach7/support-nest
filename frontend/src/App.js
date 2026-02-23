import React, { useEffect, useState } from 'react';
import SubmitTicket from './components/SubmitTicket';
import TicketList from './components/TicketList';
import StatsDashboard from './components/StatsDashboard';
import { ticketAPI } from './api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [theme, setTheme] = useState(localStorage.getItem('supportnest-theme') || 'dark');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('supportnest-theme', theme);
  }, [theme]);

  useEffect(() => {
    if (activeTab === 'home') {
      fetchDashboardStats();
    }
  }, [activeTab, refreshTrigger]);

  const fetchDashboardStats = async () => {
    setStatsLoading(true);
    try {
      const response = await ticketAPI.getStats();
      setDashboardStats(response.data);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    } finally {
      setStatsLoading(false);
    }
  };

  const handleTicketCreated = (newTicket) => {
    // Trigger refresh of ticket list and stats
    setRefreshTrigger(prev => prev + 1);
    // Switch to ticket list to show the new ticket
    setActiveTab('tickets');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="app-brand">Support Nest</div>
        <nav className="app-nav" aria-label="Main navigation">
          <button
            className={activeTab === 'home' ? 'active' : ''}
            onClick={() => setActiveTab('home')}
          >
            Home
          </button>
          <button
            className={activeTab === 'submit' ? 'active' : ''}
            onClick={() => setActiveTab('submit')}
          >
            Submit Ticket
          </button>
          <button
            className={activeTab === 'tickets' ? 'active' : ''}
            onClick={() => setActiveTab('tickets')}
          >
            Tickets
          </button>
          <button
            className={activeTab === 'statistics' ? 'active' : ''}
            onClick={() => setActiveTab('statistics')}
          >
            Statistics
          </button>
        </nav>
        <div className="header-actions">
          <button
            className="profile-btn"
            onClick={() => setShowLoginModal(!showLoginModal)}
            title="Login / Settings"
          >
            ⌘
          </button>
          <button
            className="theme-toggle"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            aria-label="Toggle light dark mode"
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? '☾' : '☀'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'home' && (
          <>
            <section className="hero-section">
              <h1>
                Resolve every ticket faster
                <span> — together.</span>
              </h1>
              <p>
                Support Nest gives your team one clean workspace for intake, prioritization,
                ownership, and closure — powered by smart suggestions and human decisions.
              </p>
              <div className="hero-actions">
                <button type="button" className="hero-primary" onClick={() => setActiveTab('submit')}>
                  Create Ticket
                </button>
                <button type="button" className="hero-secondary" onClick={() => setActiveTab('tickets')}>
                  View Ticket Queue
                </button>
              </div>
            </section>

            <section className="content-section">
              <div className="content-block">
                <div className="content-text">
                  <h2>Built for teams that care about resolution speed</h2>
                  <p>
                    Every second counts when customers are waiting. Support Nest accelerates your response cycles
                    by intelligently categorizing incoming requests, surfacing urgent issues first, and keeping your
                    entire team synchronized on status and ownership. No more lost context. No more duplicate effort.
                  </p>
                  <ul className="content-list">
                    <li>Instant category and priority suggestions from request text</li>
                    <li>Unified queue view for all team members</li>
                    <li>Search-first workflow to prevent duplicate tickets</li>
                  </ul>
                </div>
                <div className="content-visual">
                  {statsLoading ? (
                    <div className="queue-dashboard loading">
                      <p>Loading queue status...</p>
                    </div>
                  ) : dashboardStats ? (
                    <div className="queue-dashboard">
                      <div className="dashboard-header">
                        <h3>Queue Status</h3>
                      </div>
                      <div className="dashboard-metrics">
                        <div className="metric">
                          <div className="metric-value">{dashboardStats.total_tickets}</div>
                          <div className="metric-label">Total Tickets</div>
                        </div>
                        <div className="metric">
                          <div className="metric-value">{dashboardStats.open_tickets}</div>
                          <div className="metric-label">Open</div>
                        </div>
                        <div className="metric">
                          <div className="metric-value">{dashboardStats.avg_tickets_per_day}</div>
                          <div className="metric-label">Per Day</div>
                        </div>
                      </div>
                      <div className="dashboard-priorities">
                        <h4>By Priority</h4>
                        <div className="priority-bars">
                          {dashboardStats.priority_breakdown && Object.entries(dashboardStats.priority_breakdown).map(([priority, count]) => (
                            <div key={priority} className={`priority-bar priority-${priority}`}>
                              <div className="bar-label">{priority}</div>
                              <div className="bar-value">{count}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="queue-dashboard empty">
                      <p>No tickets yet</p>
                    </div>
                  )}
                </div>
              </div>
            </section>

            <section className="feature-section">
              <h2>Designed for high-performance support teams</h2>
              <div className="feature-grid">
                <article className="feature-card">
                  <div className="card-icon">🎯</div>
                  <h3>Context-Aware Intake</h3>
                  <p>Every request is captured with intelligent category and priority suggestions powered by AI analysis.</p>
                </article>
                <article className="feature-card">
                  <div className="card-icon">📊</div>
                  <h3>Queue Clarity</h3>
                  <p>One unified view of all tickets. See what's open, in-progress, blocked, and ready to close at a glance.</p>
                </article>
                <article className="feature-card">
                  <div className="card-icon">📈</div>
                  <h3>Live Metrics</h3>
                  <p>Real-time insights on ticket volume, priority distribution, and team performance trends.</p>
                </article>
              </div>
            </section>
          </>
        )}

        {activeTab === 'submit' && <SubmitTicket onTicketCreated={handleTicketCreated} />}
        {activeTab === 'tickets' && <TicketList refreshTrigger={refreshTrigger} />}
        {activeTab === 'statistics' && <StatsDashboard refreshTrigger={refreshTrigger} />}
      </main>

      {showLoginModal && (
        <div className="modal-overlay" onClick={() => setShowLoginModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Login / Settings</h2>
              <button
                className="modal-close"
                onClick={() => setShowLoginModal(false)}
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p>Welcome to Support Nest. This demo interface does not require authentication.</p>
              <p>In a production environment, you would log in here with your team credentials.</p>
              <div className="demo-info">
                <h3>Admin Demo</h3>
                <p><strong>Email:</strong> admin@supportnest.local</p>
                <p><strong>Password:</strong> (demo mode - no password required)</p>
              </div>
              <button
                className="modal-action-btn"
                onClick={() => setShowLoginModal(false)}
              >
                Continue to Dashboard
              </button>
            </div>
          </div>
        </div>
      )}

      <footer className="app-footer">
        <p>Support Nest - Django + React + PostgreSQL + Gemini</p>
      </footer>
    </div>
  );
}

export default App;
