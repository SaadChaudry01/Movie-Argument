"""Advanced analytics for the Movie Argument Engine."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import math

from models.movie import MovieDetails, MovieBasic
from models.scoring import ScoreBreakdown, WeightConfig
from .engine import ScoringEngine
from .normalizers import Normalizers


class MovieAnalytics:
    """
    Advanced analytics features for movie analysis.
    
    Provides genre-adjusted scoring, era normalization, and trend detection.
    """
    
    def __init__(self, scoring_engine: Optional[ScoringEngine] = None):
        self.scoring_engine = scoring_engine or ScoringEngine()
    
    def genre_adjusted_score(
        self,
        movie: MovieDetails,
        genre_baselines: Dict[str, float],
    ) -> Dict:
        """
        Calculate score adjusted for genre expectations.
        
        Different genres have different typical scores (e.g., documentaries
        often rate higher than horror). This adjusts for that bias.
        """
        base_breakdown = self.scoring_engine.score_movie(movie)
        
        # Calculate genre adjustment
        movie_genres = [g.name for g in movie.genres]
        if not movie_genres:
            return {
                "raw_score": base_breakdown.total_score,
                "adjusted_score": base_breakdown.total_score,
                "adjustment": 0,
                "genres": [],
                "explanation": "No genre information available",
            }
        
        # Average baseline for this movie's genres
        baselines = [
            genre_baselines.get(g, 65.0)
            for g in movie_genres
            if g in genre_baselines
        ]
        
        if baselines:
            avg_baseline = sum(baselines) / len(baselines)
        else:
            avg_baseline = 65.0  # Default baseline
        
        # Adjustment: how much above/below genre average
        adjustment = base_breakdown.total_score - avg_baseline
        
        # Adjusted score: normalized to account for genre difficulty
        # A movie scoring average for a hard genre is better than
        # a movie scoring average for an easy genre
        adjusted_score = 60 + (adjustment * 1.2)
        adjusted_score = max(0, min(100, adjusted_score))
        
        return {
            "raw_score": base_breakdown.total_score,
            "adjusted_score": round(adjusted_score, 2),
            "adjustment": round(adjustment, 2),
            "genre_baseline": round(avg_baseline, 2),
            "genres": movie_genres,
            "explanation": self._explain_genre_adjustment(
                movie.title, adjustment, movie_genres
            ),
        }
    
    def _explain_genre_adjustment(
        self,
        title: str,
        adjustment: float,
        genres: List[str],
    ) -> str:
        """Generate explanation for genre adjustment."""
        genre_str = ", ".join(genres[:2])
        
        if adjustment > 10:
            return f"{title} scores significantly above average for {genre_str} films"
        elif adjustment > 5:
            return f"{title} scores above average for {genre_str} films"
        elif adjustment > -5:
            return f"{title} scores about average for {genre_str} films"
        elif adjustment > -10:
            return f"{title} scores below average for {genre_str} films"
        else:
            return f"{title} scores significantly below average for {genre_str} films"
    
    def era_comparison(
        self,
        movie: MovieDetails,
        era_stats: Dict[int, Dict],
    ) -> Dict:
        """
        Compare movie to others from its era.
        
        Provides context for how a movie compares to its contemporaries.
        """
        year = movie.year
        if not year:
            return {
                "era": "Unknown",
                "era_percentile": 50,
                "explanation": "Release year unknown",
            }
        
        # Determine era
        if year >= 2020:
            era = "2020s"
            era_range = "2020-present"
        elif year >= 2010:
            era = "2010s"
            era_range = "2010-2019"
        elif year >= 2000:
            era = "2000s"
            era_range = "2000-2009"
        elif year >= 1990:
            era = "1990s"
            era_range = "1990-1999"
        elif year >= 1980:
            era = "1980s"
            era_range = "1980-1989"
        else:
            era = "Classic"
            era_range = "Pre-1980"
        
        # Get era statistics
        decade_start = (year // 10) * 10
        era_data = era_stats.get(decade_start, {
            "avg_rating": 6.5,
            "avg_popularity": 20,
            "count": 1000,
        })
        
        breakdown = self.scoring_engine.score_movie(movie)
        
        # Calculate percentile within era
        era_avg = era_data.get("avg_score", 65)
        era_std = era_data.get("std_score", 10)
        
        z_score = (breakdown.total_score - era_avg) / era_std if era_std > 0 else 0
        percentile = self._z_to_percentile(z_score)
        
        return {
            "year": year,
            "era": era,
            "era_range": era_range,
            "movie_score": breakdown.total_score,
            "era_average": era_avg,
            "era_percentile": round(percentile, 1),
            "explanation": self._explain_era_comparison(
                movie.title, era, percentile
            ),
        }
    
    def _z_to_percentile(self, z: float) -> float:
        """Convert z-score to percentile."""
        # Approximation using error function
        return 50 * (1 + math.erf(z / math.sqrt(2)))
    
    def _explain_era_comparison(
        self,
        title: str,
        era: str,
        percentile: float,
    ) -> str:
        """Generate explanation for era comparison."""
        if percentile >= 90:
            return f"{title} is among the top 10% of {era} films"
        elif percentile >= 75:
            return f"{title} ranks in the top quarter of {era} films"
        elif percentile >= 50:
            return f"{title} is above average for {era} films"
        elif percentile >= 25:
            return f"{title} is below average for {era} films"
        else:
            return f"{title} ranks in the bottom quarter of {era} films"
    
    def audience_critic_divergence(
        self,
        movie: MovieDetails,
        critic_score: Optional[float] = None,
    ) -> Dict:
        """
        Analyze divergence between audience and critic scores.
        
        High divergence often indicates controversial or niche films.
        """
        audience_score = movie.vote_average
        
        # If no critic score provided, estimate from movie characteristics
        if critic_score is None:
            # Estimate based on genre and other factors
            # (In production, this would come from Rotten Tomatoes API)
            critic_score = self._estimate_critic_score(movie)
        
        divergence = audience_score - critic_score
        abs_divergence = abs(divergence)
        
        if divergence > 1.5:
            category = "audience_favorite"
            explanation = f"Audiences love {movie.title} more than critics"
        elif divergence < -1.5:
            category = "critic_favorite"
            explanation = f"Critics appreciate {movie.title} more than general audiences"
        else:
            category = "consensus"
            explanation = f"Audiences and critics generally agree on {movie.title}"
        
        return {
            "audience_score": audience_score,
            "critic_score": round(critic_score, 1),
            "divergence": round(divergence, 2),
            "category": category,
            "explanation": explanation,
            "insight": self._get_divergence_insight(category, movie),
        }
    
    def _estimate_critic_score(self, movie: MovieDetails) -> float:
        """Estimate critic score from movie characteristics."""
        base = movie.vote_average
        
        # Critics tend to rate certain genres differently
        genre_adjustments = {
            "Documentary": 0.3,
            "Drama": 0.2,
            "Animation": 0.1,
            "Horror": -0.4,
            "Comedy": -0.2,
            "Action": -0.3,
        }
        
        adjustment = 0
        for genre in movie.genres:
            adjustment += genre_adjustments.get(genre.name, 0)
        
        # Average if multiple adjustments
        if movie.genres:
            adjustment /= len(movie.genres)
        
        return base + adjustment
    
    def _get_divergence_insight(self, category: str, movie: MovieDetails) -> str:
        """Get insight based on divergence category."""
        if category == "audience_favorite":
            return (
                "This film resonates strongly with general audiences, "
                "possibly due to entertainment value or emotional impact "
                "that critics may undervalue."
            )
        elif category == "critic_favorite":
            return (
                "This film showcases qualities that critics appreciate "
                "(artistic merit, innovation, performances) but may be "
                "too challenging or niche for mainstream audiences."
            )
        else:
            return (
                "Both critics and audiences see similar value in this film, "
                "suggesting broad appeal and consistent quality."
            )
    
    def franchise_analysis(
        self,
        movies: List[MovieDetails],
        franchise_name: str,
    ) -> Dict:
        """
        Analyze a franchise's performance over time.
        
        Tracks quality trends, box office, and identifies best/worst entries.
        """
        if not movies:
            return {"error": "No movies provided"}
        
        # Sort by release date
        sorted_movies = sorted(
            movies,
            key=lambda m: m.release_date or "9999",
        )
        
        # Score each entry
        entries = []
        for movie in sorted_movies:
            breakdown = self.scoring_engine.score_movie(movie)
            entries.append({
                "id": movie.id,
                "title": movie.title,
                "year": movie.year,
                "score": breakdown.total_score,
                "grade": breakdown.grade,
                "revenue": movie.revenue,
                "budget": movie.budget,
            })
        
        scores = [e["score"] for e in entries]
        
        # Find best and worst
        best_idx = scores.index(max(scores))
        worst_idx = scores.index(min(scores))
        
        # Calculate trend (is franchise improving or declining?)
        if len(scores) >= 3:
            first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            trend = "improving" if second_half_avg > first_half_avg + 2 else \
                    "declining" if second_half_avg < first_half_avg - 2 else "stable"
        else:
            trend = "insufficient_data"
        
        # Total box office
        total_revenue = sum(e["revenue"] for e in entries if e["revenue"])
        total_budget = sum(e["budget"] for e in entries if e["budget"])
        
        return {
            "franchise": franchise_name,
            "total_entries": len(entries),
            "entries": entries,
            "average_score": round(sum(scores) / len(scores), 2),
            "best_entry": entries[best_idx],
            "worst_entry": entries[worst_idx],
            "trend": trend,
            "total_revenue": total_revenue,
            "total_budget": total_budget,
            "total_profit": total_revenue - total_budget if total_budget else None,
        }
    
    def calculate_rewatchability(self, movie: MovieDetails) -> Dict:
        """
        Estimate movie rewatchability based on various factors.
        
        Some movies are more rewatchable than others due to
        complexity, entertainment value, and cultural impact.
        """
        factors = {}
        
        # Runtime factor - medium length movies are more rewatchable
        runtime = movie.runtime or 120
        if 90 <= runtime <= 130:
            factors["runtime"] = 100
        elif 80 <= runtime <= 150:
            factors["runtime"] = 80
        else:
            factors["runtime"] = 60
        
        # Genre factor - some genres are more rewatchable
        rewatchable_genres = {
            "Comedy": 90,
            "Action": 85,
            "Animation": 90,
            "Adventure": 85,
            "Science Fiction": 80,
            "Fantasy": 85,
            "Family": 90,
            "Musical": 85,
        }
        genre_scores = [
            rewatchable_genres.get(g.name, 70)
            for g in movie.genres
        ]
        factors["genre"] = sum(genre_scores) / len(genre_scores) if genre_scores else 70
        
        # Popularity factor - popular movies get rewatched more
        factors["popularity"] = Normalizers.normalize_popularity(movie.popularity)
        
        # Rating factor - higher rated movies are more rewatchable
        factors["rating"] = Normalizers.normalize_vote_average(movie.vote_average)
        
        # Calculate overall rewatchability
        weights = {
            "runtime": 0.15,
            "genre": 0.30,
            "popularity": 0.25,
            "rating": 0.30,
        }
        
        rewatchability = sum(
            factors[k] * weights[k] for k in factors
        )
        
        # Determine category
        if rewatchability >= 85:
            category = "highly_rewatchable"
            description = "A film you'll want to watch again and again"
        elif rewatchability >= 70:
            category = "rewatchable"
            description = "Worth revisiting occasionally"
        elif rewatchability >= 55:
            category = "one_time_watch"
            description = "Enjoyable but probably a one-time experience"
        else:
            category = "skip_rewatch"
            description = "Better to spend time on other films"
        
        return {
            "score": round(rewatchability, 2),
            "category": category,
            "description": description,
            "factors": {k: round(v, 2) for k, v in factors.items()},
        }
