"""Pydantic models for the Movie Argument Engine."""

from .movie import (
    Movie,
    MovieBasic,
    MovieDetails,
    CastMember,
    CrewMember,
    Genre,
)
from .scoring import (
    ScoreBreakdown,
    FeatureScore,
    WeightConfig,
    ComparisonResult,
    ArgumentPoint,
)
from .api import (
    SearchResponse,
    CompareRequest,
    CompareResponse,
    TrendingResponse,
    RecommendationsResponse,
)

__all__ = [
    "Movie",
    "MovieBasic", 
    "MovieDetails",
    "CastMember",
    "CrewMember",
    "Genre",
    "ScoreBreakdown",
    "FeatureScore",
    "WeightConfig",
    "ComparisonResult",
    "ArgumentPoint",
    "SearchResponse",
    "CompareRequest",
    "CompareResponse",
    "TrendingResponse",
    "RecommendationsResponse",
]
