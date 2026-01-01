# Annual Bowl Picks

A family bowl game prediction tracker with live odds, automatic scoring, and yearly archives.

## Features

- **Pick Tracker**: Select your picks for each bowl game
- **Live Odds**: Betting lines fetched from The Odds API
- **Auto-Locking**: Picks automatically lock at game time
- **Leaderboard**: Real-time standings showing who's winning
- **Archives**: Browse past seasons and their results
- **Admin Panel**: Import games, refresh odds, set winners

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
copy .env.example .env
# Edit .env with your settings

# Initialize database
python database.py

# (Optional) Import existing data
python scripts/import_spreadsheet.py

# Start server
python -m uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Configuration

Edit `backend/.env` with your settings:

```env
# Family password for login
FAMILY_PASSWORD=your_password_here

# The Odds API key (get free at https://the-odds-api.com/)
ODDS_API_KEY=your_api_key_here

# Secret key for sessions (generate a random string)
SECRET_KEY=change_this_to_random_string
```

## Usage

1. Open http://localhost:5173 in your browser
2. Enter the family password
3. Select your name from the dropdown
4. Click on teams to make your picks
5. View the leaderboard to see standings

### Admin Functions

- **Import Games**: Fetches bowl games from NCAA API
- **Refresh Odds**: Updates betting lines from The Odds API
- **Set Winner**: Mark game results to update scores
- **Archive Season**: Save current season and start fresh

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite
- **APIs**: NCAA API (free), The Odds API (free tier)

## Family Members

Pre-configured users:
- John, Jean, Emily, Sarah, Matt, Billy, Papa Jack, Coconut

## License

Private family project
