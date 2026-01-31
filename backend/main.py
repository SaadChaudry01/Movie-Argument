"""
Movie Argument Engine - FastAPI Backend

An end-to-end data science system for movie ranking, comparison, and analysis
with explainable AI-powered verdicts.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, List

from config import get_settings
from models.api import (
    SearchResponse,
    CompareRequest,
    CompareResponse,
    ScoreRequest,
    ScoreResponse,
    TrendingResponse,
    RecommendationsResponse,
    TopMoviesRequest,
    TopMoviesResponse,
    HealthResponse,
    ErrorResponse,
)
from models.scoring import WeightConfig, CastAnalysis
from models.movie import Movie, MovieDetails
from services.movie_service import MovieService


# Global service instance
movie_service: Optional[MovieService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global movie_service
    
    # Startup
    settings = get_settings()
    movie_service = MovieService()
    await movie_service.cache.initialize()
    
    print(f"🎬 {settings.app_name} started")
    print(f"📡 TMDB API: {'Connected' if settings.tmdb_api_key else 'No API key set'}")
    
    yield
    
    # Shutdown
    if movie_service:
        await movie_service.close()
    print("👋 Shutting down")


def get_service() -> MovieService:
    """Dependency to get movie service."""
    if movie_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return movie_service


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="End-to-end movie ranking and comparison engine with explainable AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Movie ranking and comparison engine with explainable scoring",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check(service: MovieService = Depends(get_service)):
    """Check API health status."""
    health = await service.health_check()
    return HealthResponse(
        status=health["status"],
        version="1.0.0",
        tmdb_connected=health["tmdb_connected"],
        cache_stats=health["cache_stats"],
    )


# ============================================================================
# Search & Discovery Endpoints
# ============================================================================

@app.get("/api/search", response_model=SearchResponse, tags=["Search"])
async def search_movies(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, le=500),
    year: Optional[int] = Query(None, ge=1900, le=2030),
    service: MovieService = Depends(get_service),
):
    """
    Search for movies by title.
    
    Returns paginated results with basic movie information.
    """
    try:
        return await service.search_movies(q, page, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending", response_model=TrendingResponse, tags=["Discovery"])
async def get_trending(
    time_window: str = Query("week", regex="^(day|week)$"),
    with_scores: bool = Query(False),
    service: MovieService = Depends(get_service),
):
    """
    Get trending movies.
    
    Optionally includes computed scores for each movie.
    """
    try:
        return await service.get_trending(time_window, with_scores)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/genres", tags=["Discovery"])
async def get_genres(service: MovieService = Depends(get_service)):
    """Get all available movie genres."""
    try:
        return await service.get_genres()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Movie Details Endpoints
# ============================================================================

@app.get("/api/movie/{movie_id}", tags=["Movies"])
async def get_movie(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Get detailed information about a specific movie.
    
    Includes cast, crew, genres, and financial data.
    """
    try:
        details = await service.get_movie_details(movie_id)
        return details.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Movie not found: {str(e)}")


@app.get("/api/movie/{movie_id}/similar", tags=["Movies"])
async def get_similar_movies(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """Get movies similar to the specified movie."""
    try:
        movies = await service.get_similar_movies(movie_id)
        return {"movie_id": movie_id, "similar": [m.model_dump() for m in movies]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/recommendations/{movie_id}",
    response_model=RecommendationsResponse,
    tags=["Movies"],
)
async def get_recommendations(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """Get movie recommendations based on a specific movie."""
    try:
        return await service.get_recommendations(movie_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Scoring Endpoints
# ============================================================================

@app.get("/api/score/{movie_id}", tags=["Scoring"])
async def get_movie_score(
    movie_id: int,
    vote_average_weight: float = Query(0.25, ge=0, le=1),
    vote_count_weight: float = Query(0.15, ge=0, le=1),
    popularity_weight: float = Query(0.20, ge=0, le=1),
    revenue_weight: float = Query(0.10, ge=0, le=1),
    runtime_weight: float = Query(0.05, ge=0, le=1),
    recency_weight: float = Query(0.10, ge=0, le=1),
    cast_weight: float = Query(0.15, ge=0, le=1),
    service: MovieService = Depends(get_service),
):
    """
    Get explainable score breakdown for a movie.
    
    Returns detailed feature-level attribution with customizable weights.
    Weights are automatically normalized to sum to 1.
    """
    try:
        weights = WeightConfig(
            vote_average=vote_average_weight,
            vote_count=vote_count_weight,
            popularity=popularity_weight,
            revenue=revenue_weight,
            runtime_quality=runtime_weight,
            release_recency=recency_weight,
            cast_star_power=cast_weight,
        )
        
        breakdown = await service.score_movie(movie_id, weights)
        return breakdown.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/score", tags=["Scoring"])
async def score_movie_post(
    request: ScoreRequest,
    service: MovieService = Depends(get_service),
):
    """
    Get explainable score breakdown (POST version).
    
    Allows passing weight configuration in request body.
    """
    try:
        breakdown = await service.score_movie(request.movie_id, request.weights)
        return ScoreResponse(success=True, breakdown=breakdown)
    except Exception as e:
        return ScoreResponse(success=False, error=str(e))


# ============================================================================
# Comparison Endpoints
# ============================================================================

@app.post("/api/compare", tags=["Comparison"])
async def compare_movies(
    request: CompareRequest,
    service: MovieService = Depends(get_service),
):
    """
    Compare two movies with detailed evidence-based arguments.
    
    Returns:
    - Score breakdowns for both movies
    - Winner determination with confidence level
    - Feature-by-feature comparison arguments
    - Natural language verdict
    - Visualization data for charts
    """
    try:
        comparison = await service.compare_movies(
            request.movie1_id,
            request.movie2_id,
            request.weights,
        )
        return CompareResponse(success=True, comparison=comparison)
    except Exception as e:
        return CompareResponse(success=False, error=str(e))


@app.get("/api/compare/{movie1_id}/{movie2_id}", tags=["Comparison"])
async def compare_movies_get(
    movie1_id: int,
    movie2_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Compare two movies (GET version for easy linking).
    
    Uses default weights.
    """
    try:
        comparison = await service.compare_movies(movie1_id, movie2_id)
        return comparison.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cast Analysis Endpoints
# ============================================================================

@app.get("/api/cast-analysis/{movie_id}", tags=["Analysis"])
async def analyze_cast(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Analyze the star power of a movie's cast.
    
    Returns metrics on cast popularity, star power, and depth.
    """
    try:
        analysis = await service.analyze_cast(movie_id)
        return analysis.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Top Movies Endpoints
# ============================================================================

@app.post("/api/top-movies", tags=["Discovery"])
async def get_top_movies(
    request: TopMoviesRequest,
    service: MovieService = Depends(get_service),
):
    """
    Get top movies by custom criteria.
    
    Filter by genre, year range, and minimum votes.
    Results are scored and ranked.
    """
    try:
        results = await service.get_top_movies(
            genre=request.genre,
            year_min=request.year_min,
            year_max=request.year_max,
            min_votes=request.min_votes,
            weights=request.weights,
            limit=request.limit,
        )
        return TopMoviesResponse(
            criteria={
                "genre": request.genre,
                "year_min": request.year_min,
                "year_max": request.year_max,
                "min_votes": request.min_votes,
            },
            results=results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Advanced Analytics Endpoints
# ============================================================================

@app.get("/api/analytics/rewatchability/{movie_id}", tags=["Analytics"])
async def get_rewatchability(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Calculate rewatchability score for a movie.
    
    Estimates how likely audiences are to rewatch based on
    genre, runtime, rating, and popularity.
    """
    try:
        from scoring.analytics import MovieAnalytics
        
        details = await service.get_movie_details(movie_id)
        analytics = MovieAnalytics()
        return analytics.calculate_rewatchability(details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/era-comparison/{movie_id}", tags=["Analytics"])
async def get_era_comparison(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Compare movie to others from its era/decade.
    
    Shows how the film ranks among its contemporaries.
    """
    try:
        from scoring.analytics import MovieAnalytics
        
        details = await service.get_movie_details(movie_id)
        analytics = MovieAnalytics()
        
        # Default era stats (in production, these would be calculated from data)
        era_stats = {
            2020: {"avg_score": 64, "std_score": 12},
            2010: {"avg_score": 65, "std_score": 11},
            2000: {"avg_score": 63, "std_score": 12},
            1990: {"avg_score": 66, "std_score": 10},
            1980: {"avg_score": 64, "std_score": 11},
        }
        
        return analytics.era_comparison(details, era_stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/genre-adjusted/{movie_id}", tags=["Analytics"])
async def get_genre_adjusted_score(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Get genre-adjusted score for fair cross-genre comparison.
    
    Accounts for the fact that some genres naturally score higher/lower.
    """
    try:
        from scoring.analytics import MovieAnalytics
        
        details = await service.get_movie_details(movie_id)
        analytics = MovieAnalytics()
        
        # Genre baselines (average scores by genre)
        genre_baselines = {
            "Documentary": 72,
            "Drama": 68,
            "Animation": 70,
            "Adventure": 65,
            "Comedy": 62,
            "Action": 63,
            "Horror": 58,
            "Thriller": 64,
            "Science Fiction": 65,
            "Fantasy": 66,
            "Romance": 63,
            "Crime": 67,
            "Mystery": 66,
            "Family": 64,
            "War": 69,
            "History": 70,
            "Music": 68,
            "Western": 65,
        }
        
        return analytics.genre_adjusted_score(details, genre_baselines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/divergence/{movie_id}", tags=["Analytics"])
async def get_audience_critic_divergence(
    movie_id: int,
    service: MovieService = Depends(get_service),
):
    """
    Analyze divergence between audience and critic opinions.
    
    Identifies films that audiences love but critics don't (or vice versa).
    """
    try:
        from scoring.analytics import MovieAnalytics
        
        details = await service.get_movie_details(movie_id)
        analytics = MovieAnalytics()
        
        return analytics.audience_critic_divergence(details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
