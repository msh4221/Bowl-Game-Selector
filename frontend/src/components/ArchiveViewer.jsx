import { useState, useEffect } from 'react';
import api from '../api/client';

function ArchiveViewer() {
  const [archives, setArchives] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [seasonData, setSeasonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadArchives();
  }, []);

  const loadArchives = async () => {
    try {
      const data = await api.getArchivedSeasons();
      setArchives(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSeasonData = async (year) => {
    try {
      setLoading(true);
      const data = await api.getArchivedSeason(year);
      setSeasonData(data);
      setSelectedYear(year);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setSelectedYear(null);
    setSeasonData(null);
  };

  if (loading && !seasonData) {
    return <div>Loading archives...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  // Show season detail
  if (selectedYear && seasonData) {
    return (
      <div>
        <button
          className="btn-secondary"
          onClick={handleBack}
          style={{ marginBottom: '1rem' }}
        >
          Back to Archives
        </button>

        <h2>{selectedYear} Season</h2>

        <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Final Standings</h3>
        <div className="leaderboard">
          <div className="leaderboard-header">
            <span>#</span>
            <span>Name</span>
            <span>Correct</span>
            <span>Total</span>
          </div>
          {seasonData.standings.map((entry, index) => (
            <div key={entry.user_name} className="leaderboard-row">
              <span className={index === 0 ? 'rank gold' : index === 1 ? 'rank silver' : index === 2 ? 'rank bronze' : 'rank'}>
                {index + 1}
              </span>
              <span>{entry.user_name}</span>
              <span>{entry.correct_picks}</span>
              <span>{entry.total_picks}</span>
            </div>
          ))}
        </div>

        <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Games & Picks</h3>
        {seasonData.games.map((game, index) => (
          <div key={index} className="game-card">
            <div className="game-header">
              <span className="bowl-name">{game.bowl_name}</span>
              <span style={{ color: '#10b981' }}>Winner: {game.winner}</span>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <strong>{game.away_team}</strong> vs <strong>{game.home_team}</strong>
              {game.spread && <span style={{ color: 'rgba(255,255,255,0.6)' }}> (Spread: {game.spread})</span>}
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {Object.entries(game.picks).map(([userName, pick]) => (
                <span
                  key={userName}
                  className={`score-badge ${pick.is_correct ? 'correct' : 'incorrect'}`}
                >
                  {userName}: {pick.picked_team}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Show archives list
  return (
    <div>
      <h2>Season Archives</h2>

      {archives.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>No archived seasons yet.</p>
          <p style={{ color: 'rgba(255,255,255,0.6)', marginTop: '0.5rem' }}>
            Use the Admin panel to archive the current season when it ends.
          </p>
        </div>
      ) : (
        <div className="archive-list">
          {archives.map(archive => (
            <div
              key={archive.id}
              className="archive-card"
              onClick={() => loadSeasonData(archive.year)}
            >
              <div className="archive-year">{archive.year}</div>
              <div style={{ color: 'rgba(255,255,255,0.6)' }}>
                Archived on {new Date(archive.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ArchiveViewer;
