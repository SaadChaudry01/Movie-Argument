"""Movie comparison engine with argument generation."""

from typing import Dict, List, Optional, Tuple
from models.movie import MovieDetails
from models.scoring import (
    ComparisonResult,
    ArgumentPoint,
    ScoreBreakdown,
    WeightConfig,
)
from .engine import ScoringEngine
from .normalizers import Normalizers


class MovieComparator:
    """
    Compare two movies and generate evidence-based arguments.
    
    Produces detailed, explainable verdicts with feature-level attribution.
    """
    
    def __init__(self, scoring_engine: Optional[ScoringEngine] = None):
        self.scoring_engine = scoring_engine or ScoringEngine()
    
    def compare(
        self,
        movie1: MovieDetails,
        movie2: MovieDetails,
        weights: Optional[WeightConfig] = None,
    ) -> ComparisonResult:
        """
        Compare two movies and generate comprehensive comparison result.
        """
        # Score both movies
        breakdown1 = self.scoring_engine.score_movie(movie1, weights)
        breakdown2 = self.scoring_engine.score_movie(movie2, weights)
        
        # Determine winner
        score_diff = abs(breakdown1.total_score - breakdown2.total_score)
        
        if score_diff < 2:
            winner = "tie"
            confidence = "very_close"
        elif score_diff < 5:
            winner = "movie1" if breakdown1.total_score > breakdown2.total_score else "movie2"
            confidence = "close"
        elif score_diff < 15:
            winner = "movie1" if breakdown1.total_score > breakdown2.total_score else "movie2"
            confidence = "clear"
        else:
            winner = "movie1" if breakdown1.total_score > breakdown2.total_score else "movie2"
            confidence = "decisive"
        
        # Generate arguments
        arguments = self._generate_arguments(movie1, movie2, breakdown1, breakdown2)
        
        # Generate verdict
        verdict = self._generate_verdict(
            movie1, movie2, breakdown1, breakdown2, winner, confidence
        )
        
        # Generate detailed analysis
        detailed_analysis = self._generate_detailed_analysis(
            movie1, movie2, breakdown1, breakdown2, arguments
        )
        
        # Prepare visualization data
        radar_data = self._prepare_radar_data(breakdown1, breakdown2)
        bar_data = self._prepare_bar_data(breakdown1, breakdown2)
        
        return ComparisonResult(
            movie1_id=movie1.id,
            movie1_title=movie1.title,
            movie1_score=breakdown1.total_score,
            movie1_breakdown=breakdown1,
            movie2_id=movie2.id,
            movie2_title=movie2.title,
            movie2_score=breakdown2.total_score,
            movie2_breakdown=breakdown2,
            winner=winner,
            score_difference=round(score_diff, 2),
            confidence=confidence,
            arguments=arguments,
            verdict=verdict,
            detailed_analysis=detailed_analysis,
            radar_data=radar_data,
            bar_data=bar_data,
        )
    
    def _generate_arguments(
        self,
        movie1: MovieDetails,
        movie2: MovieDetails,
        breakdown1: ScoreBreakdown,
        breakdown2: ScoreBreakdown,
    ) -> List[ArgumentPoint]:
        """Generate argument points comparing each feature."""
        arguments = []
        
        features1 = breakdown1.feature_dict
        features2 = breakdown2.feature_dict
        
        for name, feat1 in features1.items():
            feat2 = features2.get(name)
            if not feat2:
                continue
            
            diff = feat1.normalized_value - feat2.normalized_value
            abs_diff = abs(diff)
            
            # Determine winner for this feature
            if abs_diff < 5:
                feature_winner = "tie"
            elif diff > 0:
                feature_winner = "movie1"
            else:
                feature_winner = "movie2"
            
            # Determine importance
            importance = self._get_importance(abs_diff, feat1.weight)
            
            # Format values for display
            value1 = self._format_feature_value(name, feat1.raw_value, movie1)
            value2 = self._format_feature_value(name, feat2.raw_value, movie2)
            
            # Generate explanation
            explanation = self._explain_feature_comparison(
                name, feat1, feat2, movie1, movie2, feature_winner
            )
            
            arguments.append(ArgumentPoint(
                factor=feat1.display_name,
                winner=feature_winner,
                movie1_value=value1,
                movie2_value=value2,
                difference=round(diff, 2),
                importance=importance,
                explanation=explanation,
            ))
        
        # Sort by importance and difference
        importance_order = {"high": 0, "medium": 1, "low": 2}
        arguments.sort(key=lambda a: (
            importance_order.get(a.importance, 2),
            -abs(a.difference)
        ))
        
        return arguments
    
    def _get_importance(self, difference: float, weight: float) -> str:
        """Determine importance of a feature difference."""
        impact = difference * weight
        
        if impact > 10 or difference > 30:
            return "high"
        elif impact > 5 or difference > 15:
            return "medium"
        else:
            return "low"
    
    def _format_feature_value(
        self, 
        feature_name: str, 
        raw_value: float,
        movie: MovieDetails,
    ) -> str:
        """Format raw feature value for display."""
        if feature_name == "vote_average":
            return f"{raw_value:.1f}/10"
        elif feature_name == "vote_count":
            return f"{int(raw_value):,} votes"
        elif feature_name == "popularity":
            return f"{raw_value:.1f}"
        elif feature_name == "revenue":
            if raw_value > 0:
                return f"${raw_value / 1_000_000:,.0f}M"
            return "N/A"
        elif feature_name == "runtime_quality":
            runtime = movie.runtime
            if runtime:
                h, m = divmod(runtime, 60)
                return f"{h}h {m}m"
            return "N/A"
        elif feature_name == "release_recency":
            return str(int(raw_value)) if raw_value else "N/A"
        elif feature_name == "cast_star_power":
            if movie.cast:
                return f"Led by {movie.cast[0].name}"
            return "Unknown cast"
        return str(raw_value)
    
    def _explain_feature_comparison(
        self,
        feature_name: str,
        feat1,
        feat2,
        movie1: MovieDetails,
        movie2: MovieDetails,
        winner: str,
    ) -> str:
        """Generate explanation for a feature comparison."""
        diff = abs(feat1.normalized_value - feat2.normalized_value)
        
        if winner == "tie":
            return f"Both films score similarly on {feat1.display_name.lower()}"
        
        better_movie = movie1.title if winner == "movie1" else movie2.title
        
        if feature_name == "vote_average":
            better_rating = feat1.raw_value if winner == "movie1" else feat2.raw_value
            worse_rating = feat2.raw_value if winner == "movie1" else feat1.raw_value
            return f"{better_movie} has a higher user rating ({better_rating:.1f} vs {worse_rating:.1f})"
        
        elif feature_name == "vote_count":
            return f"{better_movie} has more votes, giving it a more reliable rating"
        
        elif feature_name == "popularity":
            return f"{better_movie} has greater audience awareness and cultural impact"
        
        elif feature_name == "revenue":
            return f"{better_movie} performed better at the box office"
        
        elif feature_name == "runtime_quality":
            return f"{better_movie} has a more optimal runtime for engaging storytelling"
        
        elif feature_name == "release_recency":
            return f"{better_movie} scores better on the era/recency factor"
        
        elif feature_name == "cast_star_power":
            return f"{better_movie} has higher star power in its cast"
        
        return f"{better_movie} scores higher on {feat1.display_name.lower()}"
    
    def _generate_verdict(
        self,
        movie1: MovieDetails,
        movie2: MovieDetails,
        breakdown1: ScoreBreakdown,
        breakdown2: ScoreBreakdown,
        winner: str,
        confidence: str,
    ) -> str:
        """Generate natural language verdict."""
        if winner == "tie":
            return (
                f"{movie1.title} and {movie2.title} are remarkably evenly matched. "
                f"Both films score {breakdown1.total_score:.1f}/100, making this "
                f"comparison essentially a tie. Your personal preferences should guide your choice."
            )
        
        winner_movie = movie1 if winner == "movie1" else movie2
        loser_movie = movie2 if winner == "movie1" else movie1
        winner_breakdown = breakdown1 if winner == "movie1" else breakdown2
        loser_breakdown = breakdown2 if winner == "movie1" else breakdown1
        
        diff = abs(breakdown1.total_score - breakdown2.total_score)
        
        if confidence == "decisive":
            intro = f"{winner_movie.title} decisively outperforms {loser_movie.title}"
        elif confidence == "clear":
            intro = f"{winner_movie.title} clearly edges out {loser_movie.title}"
        else:
            intro = f"{winner_movie.title} narrowly beats {loser_movie.title}"
        
        # Find the key differentiator
        winner_features = winner_breakdown.feature_dict
        loser_features = loser_breakdown.feature_dict
        
        biggest_diff_feature = None
        biggest_diff = 0
        
        for name, feat in winner_features.items():
            loser_feat = loser_features.get(name)
            if loser_feat:
                d = feat.normalized_value - loser_feat.normalized_value
                if d > biggest_diff:
                    biggest_diff = d
                    biggest_diff_feature = feat.display_name
        
        verdict = f"{intro} with a score of {winner_breakdown.total_score:.1f} vs {loser_breakdown.total_score:.1f}."
        
        if biggest_diff_feature:
            verdict += f" The biggest advantage is in {biggest_diff_feature.lower()}."
        
        # Add a caveat for close matches
        if confidence in ["close", "very_close"]:
            verdict += f" However, this is a close call and {loser_movie.title} has its own merits."
        
        return verdict
    
    def _generate_detailed_analysis(
        self,
        movie1: MovieDetails,
        movie2: MovieDetails,
        breakdown1: ScoreBreakdown,
        breakdown2: ScoreBreakdown,
        arguments: List[ArgumentPoint],
    ) -> str:
        """Generate detailed analytical comparison."""
        lines = []
        
        lines.append(f"## Detailed Analysis: {movie1.title} vs {movie2.title}\n")
        
        # Overview
        lines.append("### Overview")
        lines.append(f"- **{movie1.title}**: {breakdown1.grade} ({breakdown1.total_score:.1f}/100)")
        lines.append(f"- **{movie2.title}**: {breakdown2.grade} ({breakdown2.total_score:.1f}/100)")
        lines.append("")
        
        # Key differences
        high_importance = [a for a in arguments if a.importance == "high"]
        if high_importance:
            lines.append("### Key Differentiators")
            for arg in high_importance:
                emoji = "⭐" if arg.winner != "tie" else "🤝"
                lines.append(f"- {emoji} **{arg.factor}**: {arg.explanation}")
            lines.append("")
        
        # Strengths of each
        lines.append(f"### Strengths of {movie1.title}")
        movie1_wins = [a for a in arguments if a.winner == "movie1"]
        if movie1_wins:
            for arg in movie1_wins[:3]:
                lines.append(f"- {arg.factor}: {arg.movie1_value}")
        else:
            lines.append("- No clear advantages in this comparison")
        lines.append("")
        
        lines.append(f"### Strengths of {movie2.title}")
        movie2_wins = [a for a in arguments if a.winner == "movie2"]
        if movie2_wins:
            for arg in movie2_wins[:3]:
                lines.append(f"- {arg.factor}: {arg.movie2_value}")
        else:
            lines.append("- No clear advantages in this comparison")
        
        return "\n".join(lines)
    
    def _prepare_radar_data(
        self,
        breakdown1: ScoreBreakdown,
        breakdown2: ScoreBreakdown,
    ) -> List[Dict]:
        """Prepare data for radar chart visualization."""
        radar_data = []
        
        for feat1 in breakdown1.features:
            feat2 = breakdown2.feature_dict.get(feat1.name)
            if feat2:
                radar_data.append({
                    "feature": feat1.display_name,
                    "movie1": round(feat1.normalized_value, 1),
                    "movie2": round(feat2.normalized_value, 1),
                })
        
        return radar_data
    
    def _prepare_bar_data(
        self,
        breakdown1: ScoreBreakdown,
        breakdown2: ScoreBreakdown,
    ) -> List[Dict]:
        """Prepare data for bar chart visualization."""
        bar_data = []
        
        for feat1 in breakdown1.features:
            feat2 = breakdown2.feature_dict.get(feat1.name)
            if feat2:
                bar_data.append({
                    "feature": feat1.display_name,
                    "movie1_score": round(feat1.normalized_value, 1),
                    "movie2_score": round(feat2.normalized_value, 1),
                    "movie1_weighted": round(feat1.weighted_score, 2),
                    "movie2_weighted": round(feat2.weighted_score, 2),
                    "difference": round(feat1.normalized_value - feat2.normalized_value, 1),
                })
        
        return bar_data
