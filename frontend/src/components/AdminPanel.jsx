import { useState, useEffect } from 'react';
import api from '../api/client';

function AdminPanel({ onDataChange }) {
  const [games, setGames] = useState([]);
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showAddGame, setShowAddGame] = useState(false);
  const [newGame, setNewGame] = useState({
    bowl_name: '',
    home_team: '',
    away_team: '',
    game_time: '',
    is_playoff: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [gamesData, statusData] = await Promise.all([
        api.getGames(),
        api.getApiStatus()
      ]);
      setGames(gamesData);
      setApiStatus(statusData);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleImportGames = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.importGames();
      setMessage(result.message);
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshOdds = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await api.refreshOdds();
      setMessage(`${result.message}. API requests remaining: ${result.api_requests_remaining || 'Unknown'}`);
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleArchiveSeason = async () => {
    if (!confirm('Are you sure you want to archive the current season? This will create a new season.')) {
      return;
    }
    setLoading(true);
    setMessage('');
    try {
      const result = await api.archiveCurrentSeason();
      setMessage(result.message);
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSetWinner = async (gameId, winner, homeScore, awayScore) => {
    try {
      await api.updateGame(gameId, {
        winner,
        home_score: parseInt(homeScore) || null,
        away_score: parseInt(awayScore) || null
      });
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleAddGame = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createGame({
        ...newGame,
        game_time: newGame.game_time ? new Date(newGame.game_time).toISOString() : null
      });
      setNewGame({
        bowl_name: '',
        home_team: '',
        away_team: '',
        game_time: '',
        is_playoff: false
      });
      setShowAddGame(false);
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteGame = async (gameId) => {
    if (!confirm('Are you sure you want to delete this game? All picks will be lost.')) {
      return;
    }
    try {
      await api.deleteGame(gameId);
      await loadData();
      if (onDataChange) onDataChange();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>

      {message && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '1rem',
          background: message.startsWith('Error') ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
          color: message.startsWith('Error') ? '#ef4444' : '#10b981'
        }}>
          {message}
        </div>
      )}

      <div className="admin-section">
        <h3>Import & Sync</h3>
        <div className="admin-buttons">
          <button
            className="btn-primary"
            onClick={handleImportGames}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Import Games from NCAA'}
          </button>
          <button
            className="btn-primary"
            onClick={handleRefreshOdds}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh Betting Lines'}
          </button>
        </div>

        {apiStatus && (
          <div style={{ marginTop: '1rem', color: 'rgba(255,255,255,0.6)', fontSize: '0.9rem' }}>
            Odds API requests remaining: {apiStatus.odds_api.requests_remaining || 'Not configured'}
          </div>
        )}
      </div>

      <div className="admin-section">
        <h3>Season Management</h3>
        <div className="admin-buttons">
          <button
            className="btn-secondary"
            onClick={handleArchiveSeason}
            disabled={loading}
          >
            Archive Current Season
          </button>
        </div>
      </div>

      <div className="admin-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Games ({games.length})</h3>
          <button
            className="btn-primary"
            onClick={() => setShowAddGame(!showAddGame)}
          >
            {showAddGame ? 'Cancel' : 'Add Game Manually'}
          </button>
        </div>

        {showAddGame && (
          <form onSubmit={handleAddGame} style={{ marginTop: '1rem', marginBottom: '1rem' }}>
            <div style={{ display: 'grid', gap: '0.5rem', marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="Bowl Name"
                value={newGame.bowl_name}
                onChange={e => setNewGame({ ...newGame, bowl_name: e.target.value })}
                required
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <input
                type="text"
                placeholder="Away Team"
                value={newGame.away_team}
                onChange={e => setNewGame({ ...newGame, away_team: e.target.value })}
                required
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <input
                type="text"
                placeholder="Home Team"
                value={newGame.home_team}
                onChange={e => setNewGame({ ...newGame, home_team: e.target.value })}
                required
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <input
                type="datetime-local"
                value={newGame.game_time}
                onChange={e => setNewGame({ ...newGame, game_time: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.2)', background: 'rgba(255,255,255,0.1)', color: '#fff' }}
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={newGame.is_playoff}
                  onChange={e => setNewGame({ ...newGame, is_playoff: e.target.checked })}
                />
                Playoff Game
              </label>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              Add Game
            </button>
          </form>
        )}

        <div style={{ marginTop: '1rem' }}>
          {games.map(game => (
            <div key={game.id} className="game-card" style={{ marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: '600' }}>{game.bowl_name}</div>
                  <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
                    {game.away_team} vs {game.home_team}
                  </div>
                  {game.spread && (
                    <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.5)' }}>
                      Spread: {game.spread} | O/U: {game.over_under || 'N/A'}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteGame(game.id)}
                  style={{
                    padding: '4px 8px',
                    background: 'rgba(239,68,68,0.2)',
                    border: '1px solid #ef4444',
                    borderRadius: '4px',
                    color: '#ef4444',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                >
                  Delete
                </button>
              </div>

              {!game.winner && (
                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.9rem' }}>Set Winner:</span>
                  <button
                    className="btn-secondary"
                    style={{ padding: '4px 12px', fontSize: '0.85rem' }}
                    onClick={() => {
                      const scores = prompt(`Enter score (${game.away_team}-${game.home_team}):`, '0-0');
                      if (scores) {
                        const [away, home] = scores.split('-');
                        handleSetWinner(game.id, game.away_team, home, away);
                      }
                    }}
                  >
                    {game.away_team}
                  </button>
                  <button
                    className="btn-secondary"
                    style={{ padding: '4px 12px', fontSize: '0.85rem' }}
                    onClick={() => {
                      const scores = prompt(`Enter score (${game.away_team}-${game.home_team}):`, '0-0');
                      if (scores) {
                        const [away, home] = scores.split('-');
                        handleSetWinner(game.id, game.home_team, home, away);
                      }
                    }}
                  >
                    {game.home_team}
                  </button>
                </div>
              )}

              {game.winner && (
                <div style={{ marginTop: '0.5rem', color: '#10b981', fontSize: '0.9rem' }}>
                  Winner: {game.winner}
                  {game.home_score !== null && ` (${game.away_score}-${game.home_score})`}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AdminPanel;
