"""API request/response models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .movie import MovieBasic, Movie
from .scoring import WeightConfig, ComparisonResult, ScoreBreakdown


class SearchResponse(BaseModel):
    """Response for movie search."""
    query: str
    page: int
    total_pages: int
    total_results: int
    results: List[MovieBasic]


class CompareRequest(BaseModel):
    """Request to compare two movies."""
    movie1_id: int
    movie2_id: int
    weights: Optional[WeightConfig] = None


class CompareResponse(BaseModel):
    """Response for movie comparison."""
    success: bool
    comparison: Optional[ComparisonResult] = None
    error: Optional[str] = None


class ScoreRequest(BaseModel):
    """Request for movie scoring."""
    movie_id: int
    weights: Optional[WeightConfig] = None


class ScoreResponse(BaseModel):
    """Response for movie scoring."""
    success: bool
    breakdown: Optional[ScoreBreakdown] = None
    error: Optional[str] = None


class TrendingResponse(BaseModel):
    """Response for trending movies."""
    time_window: str  # "day" or "week"
    results: List[MovieBasic]
    scored_results: Optional[List[Dict]] = None  # With scores


class RecommendationsResponse(BaseModel):
    """Response for movie recommendations."""
    source_movie_id: int
    source_movie_title: str
    recommendations: List[MovieBasic]
    reason: str


class TopMoviesRequest(BaseModel):
    """Request for top movies by custom criteria."""
    genre: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    min_votes: int = 1000
    weights: Optional[WeightConfig] = None
    limit: int = Field(default=20, le=100)


class TopMoviesResponse(BaseModel):
    """Response for top movies."""
    criteria: Dict
    results: List[Dict]  # Movie with score


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    tmdb_connected: bool
    cache_stats: Dict


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
