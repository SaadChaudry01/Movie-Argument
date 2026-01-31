"""Movie-related Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class Genre(BaseModel):
    """Movie genre."""
    id: int
    name: str


class CastMember(BaseModel):
    """Cast member information."""
    id: int
    name: str
    character: str
    profile_path: Optional[str] = None
    popularity: float = 0.0
    order: int = 0
    known_for_department: str = "Acting"


class CrewMember(BaseModel):
    """Crew member information."""
    id: int
    name: str
    job: str
    department: str
    profile_path: Optional[str] = None
    popularity: float = 0.0


class ProductionCompany(BaseModel):
    """Production company information."""
    id: int
    name: str
    logo_path: Optional[str] = None
    origin_country: str = ""


class MovieBasic(BaseModel):
    """Basic movie information for search results."""
    id: int
    title: str
    original_title: str = ""
    overview: str = ""
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    genre_ids: List[int] = []
    adult: bool = False
    original_language: str = "en"
    
    @property
    def year(self) -> Optional[int]:
        """Extract release year."""
        if self.release_date:
            try:
                return int(self.release_date[:4])
            except (ValueError, IndexError):
                return None
        return None
    
    @property
    def poster_url(self) -> Optional[str]:
        """Get full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None


class MovieDetails(BaseModel):
    """Detailed movie information."""
    id: int
    title: str
    original_title: str = ""
    tagline: str = ""
    overview: str = ""
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    budget: int = 0
    revenue: int = 0
    status: str = "Released"
    genres: List[Genre] = []
    production_companies: List[ProductionCompany] = []
    spoken_languages: List[dict] = []
    origin_country: List[str] = []
    adult: bool = False
    original_language: str = "en"
    imdb_id: Optional[str] = None
    homepage: Optional[str] = None
    
    # Extended data (from additional API calls)
    cast: List[CastMember] = []
    crew: List[CrewMember] = []
    director: Optional[str] = None
    keywords: List[str] = []
    similar_movies: List[int] = []
    recommendations: List[int] = []
    
    @property
    def year(self) -> Optional[int]:
        """Extract release year."""
        if self.release_date:
            try:
                return int(self.release_date[:4])
            except (ValueError, IndexError):
                return None
        return None
    
    @property
    def poster_url(self) -> Optional[str]:
        """Get full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
    
    @property
    def backdrop_url(self) -> Optional[str]:
        """Get full backdrop URL."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/original{self.backdrop_path}"
        return None
    
    @property
    def genre_names(self) -> List[str]:
        """Get list of genre names."""
        return [g.name for g in self.genres]
    
    @property
    def profit(self) -> int:
        """Calculate profit."""
        return self.revenue - self.budget
    
    @property
    def roi(self) -> Optional[float]:
        """Calculate return on investment."""
        if self.budget > 0:
            return (self.revenue - self.budget) / self.budget * 100
        return None


class Movie(BaseModel):
    """Unified movie model used throughout the application."""
    id: int
    title: str
    year: Optional[int] = None
    overview: str = ""
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    runtime: Optional[int] = None
    budget: int = 0
    revenue: int = 0
    genres: List[str] = []
    director: Optional[str] = None
    cast: List[CastMember] = []
    tagline: str = ""
    imdb_id: Optional[str] = None
    
    @classmethod
    def from_details(cls, details: MovieDetails) -> "Movie":
        """Create Movie from MovieDetails."""
        return cls(
            id=details.id,
            title=details.title,
            year=details.year,
            overview=details.overview,
            poster_url=details.poster_url,
            backdrop_url=details.backdrop_url,
            vote_average=details.vote_average,
            vote_count=details.vote_count,
            popularity=details.popularity,
            runtime=details.runtime,
            budget=details.budget,
            revenue=details.revenue,
            genres=details.genre_names,
            director=details.director,
            cast=details.cast,
            tagline=details.tagline,
            imdb_id=details.imdb_id,
        )
