import { useState, useEffect } from 'react';
import api from '../api/client';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const data = await api.getLeaderboard();
      setLeaderboard(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRankClass = (index) => {
    if (index === 0) return 'rank gold';
    if (index === 1) return 'rank silver';
    if (index === 2) return 'rank bronze';
    return 'rank';
  };

  if (loading) {
    return <div>Loading leaderboard...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (leaderboard.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <p>No picks have been made yet.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Leaderboard</h2>

      <div className="leaderboard">
        <div className="leaderboard-header">
          <span>#</span>
          <span>Name</span>
          <span>Correct</span>
          <span>Pending</span>
        </div>

        {leaderboard.map((entry, index) => (
          <div key={entry.user_name} className="leaderboard-row">
            <span className={getRankClass(index)}>
              {index + 1}
            </span>
            <span>{entry.user_name}</span>
            <span>
              {entry.correct_picks} / {entry.total_picks - entry.pending_picks}
            </span>
            <span style={{ color: 'rgba(255,255,255,0.6)' }}>
              {entry.pending_picks}
            </span>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '2rem', padding: '20px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
        <h3 style={{ marginBottom: '1rem' }}>Stats</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#4f46e5' }}>
              {leaderboard.reduce((sum, e) => sum + e.correct_picks, 0)}
            </div>
            <div style={{ color: 'rgba(255,255,255,0.6)' }}>Total Correct</div>
          </div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#f59e0b' }}>
              {leaderboard.reduce((sum, e) => sum + e.pending_picks, 0)}
            </div>
            <div style={{ color: 'rgba(255,255,255,0.6)' }}>Pending</div>
          </div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: '700', color: '#10b981' }}>
              {leaderboard[0]?.correct_picks || 0}
            </div>
            <div style={{ color: 'rgba(255,255,255,0.6)' }}>Leader Score</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Leaderboard;
