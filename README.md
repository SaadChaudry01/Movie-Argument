# Movie Argument Engine

An end-to-end data science system for movie ranking, comparison, and analysis with explainable AI-powered verdicts.

## Features

### Core Functionality
- **Movie Search & Discovery**: Search millions of movies via TMDB integration
- **Head-to-Head Comparison**: Compare any two movies with detailed attribution
- **Explainable Scoring**: Transparent, weighted scoring with feature-level breakdown
- **Argument Generator**: Natural language explanations for movie verdicts

### Advanced Analytics
- **Cast Star Power Analysis**: Actor popularity and filmography metrics
- **Genre-Adjusted Scoring**: Fair comparisons across different genres
- **Trend Detection**: Identify rising and falling movies
- **Era Normalization**: Compare movies across decades fairly
- **Audience vs Critic Divergence**: Analyze when critics and audiences disagree

### Visualization
- **Radar Charts**: Multi-dimensional movie profiles
- **Score Breakdowns**: Interactive feature attribution
- **Historical Trends**: Movie performance over time
- **Comparison Dashboards**: Side-by-side analytics

## Tech Stack

### Backend
- **FastAPI**: High-performance async API framework
- **SQLite**: Local caching for API responses
- **Pydantic**: Data validation and serialization
- **TMDB API**: Comprehensive movie database

### Frontend
- **React 18**: Modern component-based UI
- **Vite**: Fast build tooling
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Interactive visualizations
- **Framer Motion**: Smooth animations

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- TMDB API Key (free at https://www.themoviedb.org/settings/api)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Set your TMDB API key
set TMDB_API_KEY=your_api_key_here
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Search movies by title |
| `/api/movie/{id}` | GET | Get detailed movie info |
| `/api/compare` | POST | Compare two movies |
| `/api/score/{id}` | GET | Get explainable score breakdown |
| `/api/trending` | GET | Get trending movies |
| `/api/recommendations/{id}` | GET | Get similar movies |
| `/api/cast-analysis/{id}` | GET | Analyze cast star power |

## Scoring Algorithm

The engine uses a weighted multi-factor scoring system:

| Factor | Default Weight | Description |
|--------|---------------|-------------|
| Vote Average | 25% | TMDB user rating (0-10) |
| Vote Count | 15% | Popularity confidence |
| Popularity | 20% | TMDB popularity index |
| Revenue | 10% | Box office performance |
| Runtime Quality | 5% | Optimal runtime scoring |
| Release Recency | 10% | Era adjustment |
| Cast Star Power | 15% | Lead actor popularity |

Users can adjust weights in real-time to see how rankings change.

## Project Structure

```
movie-argument-engine/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   ├── scoring/             # Scoring algorithms
│   └── data/                # Data fetching & caching
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API clients
│   │   └── utils/           # Helpers
│   └── public/
└── README.md
```

## Author

Built as a portfolio project demonstrating:
- End-to-end data science system design
- API development and integration
- Explainable AI/ML techniques
- Modern full-stack development
- Data visualization and analytics
