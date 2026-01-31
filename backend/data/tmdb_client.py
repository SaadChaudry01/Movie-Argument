"""TMDB API client for fetching movie data."""

import httpx
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

from models.movie import MovieBasic, MovieDetails, CastMember, CrewMember, Genre
from config import get_settings


class TMDBClient:
    """Async client for The Movie Database API."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.tmdb_api_key
        self.base_url = settings.tmdb_base_url
        self.image_base_url = settings.tmdb_image_base_url
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                params={"api_key": self.api_key},
                timeout=30.0,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to TMDB API."""
        client = await self._get_client()
        response = await client.get(endpoint, params=params or {})
        response.raise_for_status()
        return response.json()
    
    async def search_movies(
        self, 
        query: str, 
        page: int = 1,
        year: Optional[int] = None,
        include_adult: bool = False,
    ) -> Dict:
        """Search for movies by title."""
        params = {
            "query": query,
            "page": page,
            "include_adult": str(include_adult).lower(),
        }
        if year:
            params["year"] = year
        
        data = await self._get("/search/movie", params)
        
        return {
            "query": query,
            "page": data.get("page", 1),
            "total_pages": data.get("total_pages", 0),
            "total_results": data.get("total_results", 0),
            "results": [MovieBasic(**movie) for movie in data.get("results", [])],
        }
    
    async def get_movie_details(self, movie_id: int) -> MovieDetails:
        """Get detailed information about a movie."""
        # Fetch main details and credits in parallel
        details_task = self._get(f"/movie/{movie_id}")
        credits_task = self._get(f"/movie/{movie_id}/credits")
        keywords_task = self._get(f"/movie/{movie_id}/keywords")
        
        details, credits, keywords = await asyncio.gather(
            details_task, credits_task, keywords_task
        )
        
        # Parse cast
        cast = []
        for member in credits.get("cast", [])[:20]:  # Top 20 cast
            cast.append(CastMember(
                id=member.get("id", 0),
                name=member.get("name", ""),
                character=member.get("character", ""),
                profile_path=member.get("profile_path"),
                popularity=member.get("popularity", 0.0),
                order=member.get("order", 0),
                known_for_department=member.get("known_for_department", "Acting"),
            ))
        
        # Parse crew and find director
        crew = []
        director = None
        for member in credits.get("crew", []):
            if member.get("job") == "Director":
                director = member.get("name")
            crew.append(CrewMember(
                id=member.get("id", 0),
                name=member.get("name", ""),
                job=member.get("job", ""),
                department=member.get("department", ""),
                profile_path=member.get("profile_path"),
                popularity=member.get("popularity", 0.0),
            ))
        
        # Parse keywords
        keyword_list = [kw.get("name", "") for kw in keywords.get("keywords", [])]
        
        # Parse genres
        genres = [Genre(**g) for g in details.get("genres", [])]
        
        return MovieDetails(
            id=details.get("id", 0),
            title=details.get("title", ""),
            original_title=details.get("original_title", ""),
            tagline=details.get("tagline", ""),
            overview=details.get("overview", ""),
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            release_date=details.get("release_date"),
            runtime=details.get("runtime"),
            vote_average=details.get("vote_average", 0.0),
            vote_count=details.get("vote_count", 0),
            popularity=details.get("popularity", 0.0),
            budget=details.get("budget", 0),
            revenue=details.get("revenue", 0),
            status=details.get("status", "Released"),
            genres=genres,
            production_companies=details.get("production_companies", []),
            spoken_languages=details.get("spoken_languages", []),
            origin_country=details.get("origin_country", []),
            adult=details.get("adult", False),
            original_language=details.get("original_language", "en"),
            imdb_id=details.get("imdb_id"),
            homepage=details.get("homepage"),
            cast=cast,
            crew=crew[:20],  # Limit crew
            director=director,
            keywords=keyword_list,
        )
    
    async def get_trending(
        self, 
        time_window: str = "week",
        page: int = 1,
    ) -> List[MovieBasic]:
        """Get trending movies."""
        data = await self._get(f"/trending/movie/{time_window}", {"page": page})
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def get_popular(self, page: int = 1) -> List[MovieBasic]:
        """Get popular movies."""
        data = await self._get("/movie/popular", {"page": page})
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def get_top_rated(self, page: int = 1) -> List[MovieBasic]:
        """Get top rated movies."""
        data = await self._get("/movie/top_rated", {"page": page})
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def get_recommendations(
        self, 
        movie_id: int, 
        page: int = 1,
    ) -> List[MovieBasic]:
        """Get movie recommendations based on a movie."""
        data = await self._get(f"/movie/{movie_id}/recommendations", {"page": page})
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def get_similar(self, movie_id: int, page: int = 1) -> List[MovieBasic]:
        """Get similar movies."""
        data = await self._get(f"/movie/{movie_id}/similar", {"page": page})
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def discover_movies(
        self,
        page: int = 1,
        sort_by: str = "popularity.desc",
        year: Optional[int] = None,
        with_genres: Optional[str] = None,
        vote_count_gte: Optional[int] = None,
        vote_average_gte: Optional[float] = None,
    ) -> List[MovieBasic]:
        """Discover movies with filters."""
        params = {
            "page": page,
            "sort_by": sort_by,
        }
        if year:
            params["primary_release_year"] = year
        if with_genres:
            params["with_genres"] = with_genres
        if vote_count_gte:
            params["vote_count.gte"] = vote_count_gte
        if vote_average_gte:
            params["vote_average.gte"] = vote_average_gte
        
        data = await self._get("/discover/movie", params)
        return [MovieBasic(**movie) for movie in data.get("results", [])]
    
    async def get_genres(self) -> List[Genre]:
        """Get all movie genres."""
        data = await self._get("/genre/movie/list")
        return [Genre(**g) for g in data.get("genres", [])]
    
    async def get_person_details(self, person_id: int) -> Dict:
        """Get details about a person (actor/director)."""
        return await self._get(f"/person/{person_id}")
    
    async def get_person_credits(self, person_id: int) -> Dict:
        """Get movie credits for a person."""
        return await self._get(f"/person/{person_id}/movie_credits")
    
    async def health_check(self) -> bool:
        """Check if TMDB API is accessible."""
        try:
            await self._get("/configuration")
            return True
        except Exception:
            return False
