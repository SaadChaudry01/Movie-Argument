"""Core scoring engine for movies."""

from typing import Dict, List, Optional
from datetime import datetime

from models.movie import Movie, MovieDetails
from models.scoring import (
    ScoreBreakdown, 
    FeatureScore, 
    WeightConfig,
    ScoreCategory,
)
from .normalizers import Normalizers


class ScoringEngine:
    """
    Explainable scoring engine for movies.
    
    Produces transparent, weighted scores with feature-level attribution.
    """
    
    DEFAULT_WEIGHTS = WeightConfig()
    
    def __init__(self, weights: Optional[WeightConfig] = None):
        self.weights = weights.normalize() if weights else self.DEFAULT_WEIGHTS
        self.normalizers = Normalizers()
    
    def score_movie(
        self, 
        movie: MovieDetails,
        weights: Optional[WeightConfig] = None,
    ) -> ScoreBreakdown:
        """
        Calculate comprehensive score breakdown for a movie.
        
        Returns fully explainable score with feature attribution.
        """
        w = weights.normalize() if weights else self.weights
        features = []
        
        # 1. Vote Average Score
        vote_avg_raw = movie.vote_average
        vote_avg_norm = Normalizers.normalize_vote_average(vote_avg_raw)
        features.append(FeatureScore(
            name="vote_average",
            display_name="User Rating",
            raw_value=vote_avg_raw,
            normalized_value=vote_avg_norm,
            weight=w.vote_average,
            weighted_score=vote_avg_norm * w.vote_average,
            category=ScoreCategory.RATINGS,
            explanation=self._explain_vote_average(vote_avg_raw),
        ))
        
        # 2. Vote Count Score (confidence)
        vote_count_raw = movie.vote_count
        vote_count_norm = Normalizers.normalize_vote_count(vote_count_raw)
        features.append(FeatureScore(
            name="vote_count",
            display_name="Rating Confidence",
            raw_value=float(vote_count_raw),
            normalized_value=vote_count_norm,
            weight=w.vote_count,
            weighted_score=vote_count_norm * w.vote_count,
            category=ScoreCategory.RATINGS,
            explanation=self._explain_vote_count(vote_count_raw),
        ))
        
        # 3. Popularity Score
        popularity_raw = movie.popularity
        popularity_norm = Normalizers.normalize_popularity(popularity_raw)
        features.append(FeatureScore(
            name="popularity",
            display_name="Popularity",
            raw_value=popularity_raw,
            normalized_value=popularity_norm,
            weight=w.popularity,
            weighted_score=popularity_norm * w.popularity,
            category=ScoreCategory.POPULARITY,
            explanation=self._explain_popularity(popularity_raw),
        ))
        
        # 4. Revenue Score
        revenue_raw = movie.revenue
        revenue_norm = Normalizers.normalize_revenue(revenue_raw, movie.budget)
        features.append(FeatureScore(
            name="revenue",
            display_name="Box Office",
            raw_value=float(revenue_raw),
            normalized_value=revenue_norm,
            weight=w.revenue,
            weighted_score=revenue_norm * w.revenue,
            category=ScoreCategory.FINANCIAL,
            explanation=self._explain_revenue(revenue_raw, movie.budget),
        ))
        
        # 5. Runtime Quality Score
        runtime_raw = movie.runtime or 0
        runtime_norm = Normalizers.normalize_runtime(movie.runtime)
        features.append(FeatureScore(
            name="runtime_quality",
            display_name="Runtime Quality",
            raw_value=float(runtime_raw),
            normalized_value=runtime_norm,
            weight=w.runtime_quality,
            weighted_score=runtime_norm * w.runtime_quality,
            category=ScoreCategory.QUALITY,
            explanation=self._explain_runtime(movie.runtime),
        ))
        
        # 6. Release Recency Score
        recency_norm = Normalizers.normalize_release_recency(movie.release_date)
        year = movie.year or 0
        features.append(FeatureScore(
            name="release_recency",
            display_name="Era Score",
            raw_value=float(year),
            normalized_value=recency_norm,
            weight=w.release_recency,
            weighted_score=recency_norm * w.release_recency,
            category=ScoreCategory.TEMPORAL,
            explanation=self._explain_recency(movie.release_date),
        ))
        
        # 7. Cast Star Power Score
        cast_pops = [c.popularity for c in movie.cast[:10]]
        star_power_norm = Normalizers.normalize_cast_star_power(cast_pops)
        features.append(FeatureScore(
            name="cast_star_power",
            display_name="Star Power",
            raw_value=sum(cast_pops[:5]) if cast_pops else 0,
            normalized_value=star_power_norm,
            weight=w.cast_star_power,
            weighted_score=star_power_norm * w.cast_star_power,
            category=ScoreCategory.CAST,
            explanation=self._explain_star_power(movie.cast[:5]),
        ))
        
        # Calculate total score
        total_score = sum(f.weighted_score for f in features)
        
        # Identify strengths and weaknesses
        sorted_features = sorted(
            features, 
            key=lambda f: f.normalized_value, 
            reverse=True
        )
        strengths = [
            f"{f.display_name} ({f.normalized_value:.0f}/100)"
            for f in sorted_features[:3] if f.normalized_value >= 70
        ]
        weaknesses = [
            f"{f.display_name} ({f.normalized_value:.0f}/100)"
            for f in sorted_features[-3:] if f.normalized_value < 50
        ]
        
        # Generate summary
        summary = self._generate_summary(movie, total_score, features)
        
        return ScoreBreakdown(
            movie_id=movie.id,
            movie_title=movie.title,
            total_score=round(total_score, 2),
            grade=Normalizers.score_to_grade(total_score),
            features=features,
            strengths=strengths,
            weaknesses=weaknesses,
            summary=summary,
        )
    
    def _explain_vote_average(self, rating: float) -> str:
        """Generate explanation for vote average."""
        if rating >= 8.0:
            return f"Exceptional rating of {rating}/10 - among the highest rated films"
        elif rating >= 7.0:
            return f"Strong rating of {rating}/10 - well above average"
        elif rating >= 6.0:
            return f"Solid rating of {rating}/10 - generally positive reception"
        elif rating >= 5.0:
            return f"Mixed rating of {rating}/10 - polarizing opinions"
        else:
            return f"Low rating of {rating}/10 - predominantly negative reception"
    
    def _explain_vote_count(self, count: int) -> str:
        """Generate explanation for vote count."""
        if count >= 10000:
            return f"{count:,} votes - highly reliable rating with massive sample size"
        elif count >= 5000:
            return f"{count:,} votes - reliable rating with large sample"
        elif count >= 1000:
            return f"{count:,} votes - reasonably reliable rating"
        elif count >= 100:
            return f"{count:,} votes - limited sample, rating may fluctuate"
        else:
            return f"Only {count} votes - insufficient data for reliable rating"
    
    def _explain_popularity(self, popularity: float) -> str:
        """Generate explanation for popularity."""
        if popularity >= 100:
            return f"Extremely high popularity ({popularity:.1f}) - major cultural phenomenon"
        elif popularity >= 50:
            return f"Very popular ({popularity:.1f}) - significant audience interest"
        elif popularity >= 20:
            return f"Moderately popular ({popularity:.1f}) - solid audience awareness"
        elif popularity >= 5:
            return f"Low popularity ({popularity:.1f}) - limited mainstream awareness"
        else:
            return f"Very low popularity ({popularity:.1f}) - niche or unknown"
    
    def _explain_revenue(self, revenue: int, budget: int) -> str:
        """Generate explanation for revenue/box office."""
        if revenue <= 0:
            return "Box office data unavailable"
        
        rev_millions = revenue / 1_000_000
        
        if budget > 0:
            roi = (revenue - budget) / budget * 100
            bud_millions = budget / 1_000_000
            if roi >= 200:
                return f"${rev_millions:,.0f}M on ${bud_millions:,.0f}M budget - massive financial success ({roi:.0f}% ROI)"
            elif roi >= 100:
                return f"${rev_millions:,.0f}M on ${bud_millions:,.0f}M budget - profitable ({roi:.0f}% ROI)"
            elif roi >= 0:
                return f"${rev_millions:,.0f}M on ${bud_millions:,.0f}M budget - modest profit ({roi:.0f}% ROI)"
            else:
                return f"${rev_millions:,.0f}M on ${bud_millions:,.0f}M budget - financial loss ({roi:.0f}% ROI)"
        else:
            if rev_millions >= 1000:
                return f"${rev_millions:,.0f}M - blockbuster box office"
            elif rev_millions >= 100:
                return f"${rev_millions:,.0f}M - solid box office performance"
            else:
                return f"${rev_millions:,.0f}M box office"
    
    def _explain_runtime(self, runtime: Optional[int]) -> str:
        """Generate explanation for runtime."""
        if runtime is None:
            return "Runtime information unavailable"
        
        hours = runtime // 60
        mins = runtime % 60
        
        if 90 <= runtime <= 150:
            return f"{hours}h {mins}m - optimal length for engaging storytelling"
        elif runtime < 90:
            return f"{hours}h {mins}m - shorter than typical, may feel rushed"
        elif runtime <= 180:
            return f"{hours}h {mins}m - longer runtime requiring strong pacing"
        else:
            return f"{hours}h {mins}m - epic length, demands viewer commitment"
    
    def _explain_recency(self, release_date: Optional[str]) -> str:
        """Generate explanation for release recency."""
        if not release_date:
            return "Release date unknown"
        
        try:
            year = int(release_date[:4])
        except (ValueError, IndexError):
            return "Invalid release date"
        
        current_year = datetime.now().year
        age = current_year - year
        
        if age <= 1:
            return f"Released in {year} - brand new release"
        elif age <= 5:
            return f"Released in {year} - recent film ({age} years old)"
        elif age <= 10:
            return f"Released in {year} - modern film ({age} years old)"
        elif age <= 20:
            return f"Released in {year} - established film ({age} years old)"
        else:
            return f"Released in {year} - classic film ({age} years old)"
    
    def _explain_star_power(self, cast: list) -> str:
        """Generate explanation for star power."""
        if not cast:
            return "Cast information unavailable"
        
        top_names = [c.name for c in cast[:3] if c.popularity > 10]
        avg_pop = sum(c.popularity for c in cast[:5]) / len(cast[:5]) if cast else 0
        
        if top_names:
            names_str = ", ".join(top_names)
            if avg_pop > 50:
                return f"A-list cast featuring {names_str}"
            elif avg_pop > 20:
                return f"Well-known cast including {names_str}"
            else:
                return f"Cast includes {names_str}"
        else:
            return "Cast without major star recognition"
    
    def _generate_summary(
        self, 
        movie: MovieDetails, 
        score: float, 
        features: List[FeatureScore],
    ) -> str:
        """Generate natural language summary."""
        grade = Normalizers.score_to_grade(score)
        
        # Find top factor
        top_feature = max(features, key=lambda f: f.weighted_score)
        
        # Build summary
        parts = []
        
        if score >= 80:
            parts.append(f"{movie.title} is an outstanding film")
        elif score >= 70:
            parts.append(f"{movie.title} is a very good film")
        elif score >= 60:
            parts.append(f"{movie.title} is a solid film")
        elif score >= 50:
            parts.append(f"{movie.title} is an average film")
        else:
            parts.append(f"{movie.title} falls below average")
        
        parts.append(f"earning a {grade} grade ({score:.1f}/100)")
        
        parts.append(
            f"Its strongest aspect is {top_feature.display_name.lower()}"
        )
        
        if movie.director:
            parts.append(f"Directed by {movie.director}")
        
        return ". ".join(parts) + "."
