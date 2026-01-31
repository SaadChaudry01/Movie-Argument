"""Movie service for coordinating data fetching, caching, and scoring."""

from typing import Optional, List, Dict
import asyncio

from models.movie import Movie, MovieDetails, MovieBasic
from models.scoring import (
    ScoreBreakdown,
    ComparisonResult,
    WeightConfig,
    CastAnalysis,
)
from models.api import SearchResponse, TrendingResponse, RecommendationsResponse
from data.tmdb_client import TMDBClient
from data.cache import CacheManager
from scoring.engine import ScoringEngine
from scoring.comparator import MovieComparator


class MovieService:
    """
    Main service orchestrating movie data operations.
    
    Handles caching, API calls, scoring, and comparisons.
    """
    
    def __init__(
        self,
        tmdb_client: Optional[TMDBClient] = None,
        cache: Optional[CacheManager] = None,
    ):
        self.tmdb = tmdb_client or TMDBClient()
        self.cache = cache or CacheManager()
        self.scoring_engine = ScoringEngine()
        self.comparator = MovieComparator(self.scoring_engine)
    
    async def search_movies(
        self,
        query: str,
        page: int = 1,
        year: Optional[int] = None,
    ) -> SearchResponse:
        """Search for movies by title."""
        # Check cache first
        cache_key = f"search:{query}:{page}:{year}"
        cached = await self.cache.get_search(cache_key)
        if cached:
            return SearchResponse(**cached)
        
        # Fetch from API
        result = await self.tmdb.search_movies(query, page, year)
        
        # Cache the result
        await self.cache.set_search(cache_key, result)
        
        return SearchResponse(**result)
    
    async def get_movie_details(self, movie_id: int) -> MovieDetails:
        """Get detailed movie information with caching."""
        # Check cache
        cached = await self.cache.get_movie(movie_id)
        if cached:
            return MovieDetails(**cached)
        
        # Fetch from API
        details = await self.tmdb.get_movie_details(movie_id)
        
        # Cache the result
        await self.cache.set_movie(movie_id, details.model_dump())
        
        return details
    
    async def get_movie(self, movie_id: int) -> Movie:
        """Get unified movie model."""
        details = await self.get_movie_details(movie_id)
        return Movie.from_details(details)
    
    async def score_movie(
        self,
        movie_id: int,
        weights: Optional[WeightConfig] = None,
    ) -> ScoreBreakdown:
        """Get explainable score breakdown for a movie."""
        details = await self.get_movie_details(movie_id)
        return self.scoring_engine.score_movie(details, weights)
    
    async def compare_movies(
        self,
        movie1_id: int,
        movie2_id: int,
        weights: Optional[WeightConfig] = None,
    ) -> ComparisonResult:
        """Compare two movies with detailed arguments."""
        # Fetch both movies in parallel
        movie1, movie2 = await asyncio.gather(
            self.get_movie_details(movie1_id),
            self.get_movie_details(movie2_id),
        )
        
        # Compare
        return self.comparator.compare(movie1, movie2, weights)
    
    async def get_trending(
        self,
        time_window: str = "week",
        with_scores: bool = False,
    ) -> TrendingResponse:
        """Get trending movies with optional scores."""
        movies = await self.tmdb.get_trending(time_window)
        
        scored_results = None
        if with_scores:
            # Score trending movies
            scored_results = []
            for movie_basic in movies[:10]:  # Limit for performance
                try:
                    details = await self.get_movie_details(movie_basic.id)
                    breakdown = self.scoring_engine.score_movie(details)
                    scored_results.append({
                        "movie": movie_basic.model_dump(),
                        "score": breakdown.total_score,
                        "grade": breakdown.grade,
                    })
                except Exception:
                    pass  # Skip movies with errors
        
        return TrendingResponse(
            time_window=time_window,
            results=movies,
            scored_results=scored_results,
        )
    
    async def get_recommendations(
        self,
        movie_id: int,
        include_scores: bool = False,
    ) -> RecommendationsResponse:
        """Get movie recommendations."""
        source = await self.get_movie_details(movie_id)
        recommendations = await self.tmdb.get_recommendations(movie_id)
        
        return RecommendationsResponse(
            source_movie_id=movie_id,
            source_movie_title=source.title,
            recommendations=recommendations,
            reason=f"Movies similar to {source.title}",
        )
    
    async def get_similar_movies(self, movie_id: int) -> List[MovieBasic]:
        """Get similar movies."""
        return await self.tmdb.get_similar(movie_id)
    
    async def analyze_cast(self, movie_id: int) -> CastAnalysis:
        """Analyze the star power of a movie's cast."""
        details = await self.get_movie_details(movie_id)
        
        if not details.cast:
            return CastAnalysis(
                movie_id=movie_id,
                movie_title=details.title,
                total_star_power=0,
                average_cast_popularity=0,
                top_billed_popularity=0,
                cast_depth_score=0,
                notable_actors=[],
                analysis_text="No cast information available.",
            )
        
        # Calculate metrics
        popularities = [c.popularity for c in details.cast]
        total_star_power = sum(popularities[:10])
        avg_popularity = sum(popularities) / len(popularities) if popularities else 0
        top_billed = popularities[0] if popularities else 0
        
        # Cast depth: how many actors have > 10 popularity
        notable_count = len([p for p in popularities if p > 10])
        cast_depth = min(100, notable_count * 15)
        
        # Notable actors
        notable_actors = [
            {
                "name": c.name,
                "character": c.character,
                "popularity": c.popularity,
                "rank": i + 1,
            }
            for i, c in enumerate(details.cast[:10])
            if c.popularity > 5
        ]
        
        # Generate analysis text
        if total_star_power > 200:
            power_level = "exceptional"
        elif total_star_power > 100:
            power_level = "strong"
        elif total_star_power > 50:
            power_level = "moderate"
        else:
            power_level = "limited"
        
        lead_actor = details.cast[0].name if details.cast else "Unknown"
        
        analysis_text = (
            f"{details.title} features a cast with {power_level} star power. "
            f"Led by {lead_actor} ({top_billed:.1f} popularity), the film "
            f"has {notable_count} notable actors in its cast. "
            f"The average cast popularity is {avg_popularity:.1f}."
        )
        
        return CastAnalysis(
            movie_id=movie_id,
            movie_title=details.title,
            total_star_power=round(total_star_power, 2),
            average_cast_popularity=round(avg_popularity, 2),
            top_billed_popularity=round(top_billed, 2),
            cast_depth_score=round(cast_depth, 2),
            notable_actors=notable_actors,
            analysis_text=analysis_text,
        )
    
    async def get_top_movies(
        self,
        genre: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_votes: int = 1000,
        weights: Optional[WeightConfig] = None,
        limit: int = 20,
    ) -> List[Dict]:
        """Get top movies by custom criteria with scoring."""
        # Use discover endpoint
        movies = await self.tmdb.discover_movies(
            vote_count_gte=min_votes,
            with_genres=genre,
            year=year_min,
        )
        
        # Score each movie
        results = []
        for movie_basic in movies[:limit]:
            try:
                details = await self.get_movie_details(movie_basic.id)
                breakdown = self.scoring_engine.score_movie(details, weights)
                results.append({
                    "movie": Movie.from_details(details).model_dump(),
                    "score": breakdown.total_score,
                    "grade": breakdown.grade,
                    "top_strength": breakdown.strengths[0] if breakdown.strengths else None,
                })
            except Exception:
                pass
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    async def get_genres(self) -> List[Dict]:
        """Get all movie genres."""
        genres = await self.tmdb.get_genres()
        return [g.model_dump() for g in genres]
    
    async def health_check(self) -> Dict:
        """Check service health."""
        tmdb_ok = await self.tmdb.health_check()
        cache_stats = await self.cache.get_stats()
        
        return {
            "status": "healthy" if tmdb_ok else "degraded",
            "tmdb_connected": tmdb_ok,
            "cache_stats": cache_stats,
        }
    
    async def close(self):
        """Close connections."""
        await self.tmdb.close()
