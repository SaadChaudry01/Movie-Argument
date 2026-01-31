"""Scoring-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class ScoreCategory(str, Enum):
    """Categories for scoring factors."""
    RATINGS = "ratings"
    POPULARITY = "popularity"
    FINANCIAL = "financial"
    QUALITY = "quality"
    CAST = "cast"
    TEMPORAL = "temporal"


class FeatureScore(BaseModel):
    """Individual feature score with explanation."""
    name: str
    display_name: str
    raw_value: float
    normalized_value: float  # 0-100 scale
    weight: float
    weighted_score: float
    category: ScoreCategory
    explanation: str
    comparison_text: Optional[str] = None  # For comparisons
    
    class Config:
        use_enum_values = True


class ScoreBreakdown(BaseModel):
    """Complete score breakdown for a movie."""
    movie_id: int
    movie_title: str
    total_score: float  # 0-100 scale
    grade: str  # A+, A, B+, etc.
    features: List[FeatureScore]
    strengths: List[str]
    weaknesses: List[str]
    summary: str
    
    @property
    def feature_dict(self) -> Dict[str, FeatureScore]:
        """Get features as dictionary."""
        return {f.name: f for f in self.features}


class WeightConfig(BaseModel):
    """User-configurable scoring weights."""
    vote_average: float = Field(default=0.25, ge=0, le=1)
    vote_count: float = Field(default=0.15, ge=0, le=1)
    popularity: float = Field(default=0.20, ge=0, le=1)
    revenue: float = Field(default=0.10, ge=0, le=1)
    runtime_quality: float = Field(default=0.05, ge=0, le=1)
    release_recency: float = Field(default=0.10, ge=0, le=1)
    cast_star_power: float = Field(default=0.15, ge=0, le=1)
    
    def normalize(self) -> "WeightConfig":
        """Normalize weights to sum to 1."""
        total = (
            self.vote_average + self.vote_count + self.popularity +
            self.revenue + self.runtime_quality + self.release_recency +
            self.cast_star_power
        )
        if total == 0:
            return WeightConfig()
        
        return WeightConfig(
            vote_average=self.vote_average / total,
            vote_count=self.vote_count / total,
            popularity=self.popularity / total,
            revenue=self.revenue / total,
            runtime_quality=self.runtime_quality / total,
            release_recency=self.release_recency / total,
            cast_star_power=self.cast_star_power / total,
        )
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "popularity": self.popularity,
            "revenue": self.revenue,
            "runtime_quality": self.runtime_quality,
            "release_recency": self.release_recency,
            "cast_star_power": self.cast_star_power,
        }


class ArgumentPoint(BaseModel):
    """A single argument point in a comparison."""
    factor: str
    winner: str  # "movie1", "movie2", or "tie"
    movie1_value: str
    movie2_value: str
    difference: float
    importance: str  # "high", "medium", "low"
    explanation: str


class ComparisonResult(BaseModel):
    """Result of comparing two movies."""
    movie1_id: int
    movie1_title: str
    movie1_score: float
    movie1_breakdown: ScoreBreakdown
    
    movie2_id: int
    movie2_title: str
    movie2_score: float
    movie2_breakdown: ScoreBreakdown
    
    winner: str  # "movie1", "movie2", or "tie"
    score_difference: float
    confidence: str  # "decisive", "clear", "close", "very_close"
    
    arguments: List[ArgumentPoint]
    verdict: str  # Natural language verdict
    detailed_analysis: str
    
    # Visual data
    radar_data: List[Dict]  # For radar chart
    bar_data: List[Dict]  # For bar chart comparison


class CastAnalysis(BaseModel):
    """Analysis of a movie's cast."""
    movie_id: int
    movie_title: str
    total_star_power: float
    average_cast_popularity: float
    top_billed_popularity: float
    cast_depth_score: float
    notable_actors: List[Dict]
    analysis_text: str
