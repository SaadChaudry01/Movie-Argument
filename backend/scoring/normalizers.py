"""Normalization functions for scoring features."""

import math
from typing import Optional
from datetime import datetime


class Normalizers:
    """Collection of normalization functions for different metrics."""
    
    # Reference values for normalization (based on TMDB data distributions)
    MAX_VOTE_COUNT = 30000  # Approximate max for blockbusters
    MAX_POPULARITY = 500.0  # High popularity threshold
    MAX_REVENUE = 3_000_000_000  # ~$3B (highest grossing films)
    MAX_BUDGET = 400_000_000  # ~$400M (highest budgets)
    OPTIMAL_RUNTIME_MIN = 90
    OPTIMAL_RUNTIME_MAX = 150
    
    @staticmethod
    def normalize_vote_average(vote_average: float) -> float:
        """
        Normalize vote average (0-10 scale) to 0-100.
        Uses a slight curve to reward higher ratings more.
        """
        if vote_average <= 0:
            return 0.0
        
        # Clamp to valid range
        vote_average = min(max(vote_average, 0), 10)
        
        # Linear conversion with slight boost for high ratings
        base_score = vote_average * 10
        
        # Apply slight curve: scores above 7 get boosted
        if vote_average > 7:
            bonus = (vote_average - 7) * 3  # Up to 9 points bonus
            base_score = min(100, base_score + bonus)
        
        return round(base_score, 2)
    
    @staticmethod
    def normalize_vote_count(vote_count: int) -> float:
        """
        Normalize vote count using logarithmic scaling.
        More votes = more confidence in the rating.
        """
        if vote_count <= 0:
            return 0.0
        
        # Log scaling with reference point
        # 10,000 votes ≈ 80 score, 30,000+ ≈ 95-100
        log_count = math.log10(vote_count + 1)
        max_log = math.log10(Normalizers.MAX_VOTE_COUNT + 1)
        
        normalized = (log_count / max_log) * 100
        
        # Apply diminishing returns curve
        return round(min(100, normalized * 1.1), 2)
    
    @staticmethod
    def normalize_popularity(popularity: float) -> float:
        """
        Normalize TMDB popularity score using log scaling.
        Popularity is highly variable, so we use percentile-like scaling.
        """
        if popularity <= 0:
            return 0.0
        
        # Log scaling for popularity
        log_pop = math.log10(popularity + 1)
        max_log = math.log10(Normalizers.MAX_POPULARITY + 1)
        
        normalized = (log_pop / max_log) * 100
        
        return round(min(100, normalized), 2)
    
    @staticmethod
    def normalize_revenue(revenue: int, budget: int = 0) -> float:
        """
        Normalize revenue considering ROI if budget is available.
        Combines absolute revenue with profitability.
        """
        if revenue <= 0:
            return 25.0  # Base score for unknown revenue
        
        # Absolute revenue component (log scaled)
        log_rev = math.log10(revenue + 1)
        max_log = math.log10(Normalizers.MAX_REVENUE + 1)
        absolute_score = (log_rev / max_log) * 100
        
        # ROI component if budget is known
        if budget > 0:
            roi = (revenue - budget) / budget
            # ROI scoring: 0% = 40, 100% = 60, 500% = 100
            if roi >= 5:
                roi_score = 100
            elif roi >= 0:
                roi_score = 40 + (roi / 5) * 60
            else:
                roi_score = max(0, 40 + roi * 40)
            
            # Combine: 60% absolute, 40% ROI
            combined = absolute_score * 0.6 + roi_score * 0.4
        else:
            combined = absolute_score
        
        return round(min(100, combined), 2)
    
    @staticmethod
    def normalize_runtime(runtime: Optional[int]) -> float:
        """
        Score runtime based on optimal movie length.
        Sweet spot is generally 90-150 minutes.
        """
        if runtime is None or runtime <= 0:
            return 50.0  # Neutral score for unknown
        
        optimal_min = Normalizers.OPTIMAL_RUNTIME_MIN
        optimal_max = Normalizers.OPTIMAL_RUNTIME_MAX
        
        if optimal_min <= runtime <= optimal_max:
            # In the sweet spot
            return 100.0
        elif runtime < optimal_min:
            # Too short - might feel rushed
            penalty = (optimal_min - runtime) / optimal_min * 50
            return max(30, 100 - penalty)
        else:
            # Too long - might feel drawn out
            excess = runtime - optimal_max
            penalty = (excess / 60) * 30  # Lose 30 points per extra hour
            return max(30, 100 - penalty)
    
    @staticmethod
    def normalize_release_recency(
        release_date: Optional[str],
        favor_recent: bool = False,
    ) -> float:
        """
        Score based on release date.
        Can optionally favor recent releases.
        """
        if not release_date:
            return 50.0  # Neutral for unknown
        
        try:
            release_year = int(release_date[:4])
        except (ValueError, IndexError):
            return 50.0
        
        current_year = datetime.now().year
        age = current_year - release_year
        
        if favor_recent:
            # Recent movies score higher
            if age <= 2:
                return 100.0
            elif age <= 5:
                return 90.0
            elif age <= 10:
                return 75.0
            elif age <= 20:
                return 60.0
            else:
                return max(30, 60 - (age - 20) * 0.5)
        else:
            # Neutral scoring - classics aren't penalized
            # But give a slight boost to established classics
            if age >= 20:
                # Classic status - films that have stood the test of time
                return 75.0
            elif age >= 10:
                return 65.0
            elif age <= 2:
                return 60.0  # New, unproven
            else:
                return 70.0
    
    @staticmethod
    def normalize_cast_star_power(cast_popularities: list[float]) -> float:
        """
        Calculate star power score based on cast popularity.
        Weights top-billed actors more heavily.
        """
        if not cast_popularities:
            return 30.0  # Base score for unknown cast
        
        # Weights for cast positions (1st billed is most important)
        weights = [0.35, 0.25, 0.15, 0.10, 0.05, 0.05, 0.03, 0.02]
        
        # Pad weights if cast is longer
        while len(weights) < len(cast_popularities):
            weights.append(0.01)
        
        weighted_sum = 0.0
        for i, pop in enumerate(cast_popularities[:len(weights)]):
            # Normalize individual popularity (log scale)
            if pop > 0:
                norm_pop = min(100, math.log10(pop + 1) * 50)
            else:
                norm_pop = 0
            weighted_sum += norm_pop * weights[i]
        
        # Scale to 0-100
        total_weight = sum(weights[:len(cast_popularities)])
        if total_weight > 0:
            score = weighted_sum / total_weight
        else:
            score = 0
        
        return round(min(100, score * 1.2), 2)  # Slight boost
    
    @staticmethod
    def calculate_confidence(vote_count: int, popularity: float) -> str:
        """
        Calculate confidence level in the movie's scores.
        """
        if vote_count >= 10000 and popularity >= 50:
            return "very_high"
        elif vote_count >= 5000 and popularity >= 20:
            return "high"
        elif vote_count >= 1000 and popularity >= 10:
            return "medium"
        elif vote_count >= 100:
            return "low"
        else:
            return "very_low"
    
    @staticmethod
    def score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D+"
        elif score >= 45:
            return "D"
        elif score >= 40:
            return "D-"
        else:
            return "F"
