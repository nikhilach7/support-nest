import React, { useState } from 'react';
import SubmitTicket from './components/SubmitTicket';
import TicketList from './components/TicketList';
import StatsDashboard from './components/StatsDashboard';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('submit');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTicketCreated = (newTicket) => {
    // Trigger refresh of ticket list and stats
    setRefreshTrigger(prev => prev + 1);
    // Switch to ticket list to show the new ticket
    setActiveTab('list');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🪺 Support Nest</h1>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'submit' ? 'active' : ''}
          onClick={() => setActiveTab('submit')}
        >
          Submit Ticket
        </button>
        <button
          className={activeTab === 'list' ? 'active' : ''}
          onClick={() => setActiveTab('list')}
        >
          All Tickets
        </button>
        <button
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          Statistics
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'submit' && <SubmitTicket onTicketCreated={handleTicketCreated} />}
        {activeTab === 'list' && <TicketList refreshTrigger={refreshTrigger} />}
        {activeTab === 'stats' && <StatsDashboard refreshTrigger={refreshTrigger} />}
      </main>

      <footer className="app-footer">
        <p>Support Nest - Django + React + PostgreSQL + Gemini</p>
      </footer>
    </div>
  );
}

export default App;
