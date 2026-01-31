import type {
  SearchResponse,
  MovieDetails,
  ScoreBreakdown,
  ComparisonResult,
  WeightConfig,
  MovieBasic,
} from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new ApiError(response.status, error.error || error.detail || 'Request failed');
  }

  return response.json();
}

// Search movies
export async function searchMovies(query: string, page = 1): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, page: String(page) });
  return fetchApi<SearchResponse>(`/search?${params}`);
}

// Get movie details
export async function getMovie(movieId: number): Promise<MovieDetails> {
  return fetchApi<MovieDetails>(`/movie/${movieId}`);
}

// Get movie score breakdown
export async function getMovieScore(
  movieId: number,
  weights?: WeightConfig
): Promise<ScoreBreakdown> {
  const params = new URLSearchParams();
  
  if (weights) {
    params.set('vote_average_weight', String(weights.vote_average));
    params.set('vote_count_weight', String(weights.vote_count));
    params.set('popularity_weight', String(weights.popularity));
    params.set('revenue_weight', String(weights.revenue));
    params.set('runtime_weight', String(weights.runtime_quality));
    params.set('recency_weight', String(weights.release_recency));
    params.set('cast_weight', String(weights.cast_star_power));
  }
  
  return fetchApi<ScoreBreakdown>(`/score/${movieId}?${params}`);
}

// Compare two movies
export async function compareMovies(
  movie1Id: number,
  movie2Id: number,
  weights?: WeightConfig
): Promise<ComparisonResult> {
  const response = await fetchApi<{ success: boolean; comparison: ComparisonResult; error?: string }>(
    '/compare',
    {
      method: 'POST',
      body: JSON.stringify({
        movie1_id: movie1Id,
        movie2_id: movie2Id,
        weights,
      }),
    }
  );
  
  if (!response.success || !response.comparison) {
    throw new Error(response.error || 'Comparison failed');
  }
  
  return response.comparison;
}

// Get trending movies
export async function getTrending(
  timeWindow: 'day' | 'week' = 'week',
  withScores = false
): Promise<{ results: MovieBasic[]; scored_results?: Array<{ movie: MovieBasic; score: number; grade: string }> }> {
  const params = new URLSearchParams({
    time_window: timeWindow,
    with_scores: String(withScores),
  });
  return fetchApi(`/trending?${params}`);
}

// Get recommendations
export async function getRecommendations(movieId: number): Promise<{
  source_movie_id: number;
  source_movie_title: string;
  recommendations: MovieBasic[];
}> {
  return fetchApi(`/recommendations/${movieId}`);
}

// Get cast analysis
export async function getCastAnalysis(movieId: number): Promise<{
  movie_id: number;
  movie_title: string;
  total_star_power: number;
  average_cast_popularity: number;
  notable_actors: Array<{ name: string; character: string; popularity: number }>;
  analysis_text: string;
}> {
  return fetchApi(`/cast-analysis/${movieId}`);
}

// Get genres
export async function getGenres(): Promise<Array<{ id: number; name: string }>> {
  return fetchApi('/genres');
}

// Health check
export async function healthCheck(): Promise<{
  status: string;
  version: string;
  tmdb_connected: boolean;
}> {
  return fetchApi('/health');
}

// Utility: Get poster URL
export function getPosterUrl(path: string | null, size: 'w185' | 'w342' | 'w500' | 'original' = 'w342'): string {
  if (!path) {
    return 'https://via.placeholder.com/342x513?text=No+Poster';
  }
  return `https://image.tmdb.org/t/p/${size}${path}`;
}

// Utility: Get backdrop URL
export function getBackdropUrl(path: string | null, size: 'w780' | 'w1280' | 'original' = 'w1280'): string {
  if (!path) {
    return '';
  }
  return `https://image.tmdb.org/t/p/${size}${path}`;
}
