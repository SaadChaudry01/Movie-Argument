// Movie types
export interface MovieBasic {
  id: number;
  title: string;
  original_title: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  release_date: string | null;
  vote_average: number;
  vote_count: number;
  popularity: number;
  genre_ids: number[];
}

export interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
  popularity: number;
  order: number;
}

export interface Genre {
  id: number;
  name: string;
}

export interface MovieDetails extends MovieBasic {
  tagline: string;
  runtime: number | null;
  budget: number;
  revenue: number;
  status: string;
  genres: Genre[];
  cast: CastMember[];
  director: string | null;
  imdb_id: string | null;
  poster_url: string | null;
  backdrop_url: string | null;
}

// Scoring types
export interface FeatureScore {
  name: string;
  display_name: string;
  raw_value: number;
  normalized_value: number;
  weight: number;
  weighted_score: number;
  category: string;
  explanation: string;
}

export interface ScoreBreakdown {
  movie_id: number;
  movie_title: string;
  total_score: number;
  grade: string;
  features: FeatureScore[];
  strengths: string[];
  weaknesses: string[];
  summary: string;
}

export interface ArgumentPoint {
  factor: string;
  winner: 'movie1' | 'movie2' | 'tie';
  movie1_value: string;
  movie2_value: string;
  difference: number;
  importance: 'high' | 'medium' | 'low';
  explanation: string;
}

export interface ComparisonResult {
  movie1_id: number;
  movie1_title: string;
  movie1_score: number;
  movie1_breakdown: ScoreBreakdown;
  movie2_id: number;
  movie2_title: string;
  movie2_score: number;
  movie2_breakdown: ScoreBreakdown;
  winner: 'movie1' | 'movie2' | 'tie';
  score_difference: number;
  confidence: 'decisive' | 'clear' | 'close' | 'very_close';
  arguments: ArgumentPoint[];
  verdict: string;
  detailed_analysis: string;
  radar_data: RadarDataPoint[];
  bar_data: BarDataPoint[];
}

export interface RadarDataPoint {
  feature: string;
  movie1: number;
  movie2: number;
}

export interface BarDataPoint {
  feature: string;
  movie1_score: number;
  movie2_score: number;
  difference: number;
}

// API response types
export interface SearchResponse {
  query: string;
  page: number;
  total_pages: number;
  total_results: number;
  results: MovieBasic[];
}

export interface CompareResponse {
  success: boolean;
  comparison: ComparisonResult | null;
  error: string | null;
}

// Weight configuration
export interface WeightConfig {
  vote_average: number;
  vote_count: number;
  popularity: number;
  revenue: number;
  runtime_quality: number;
  release_recency: number;
  cast_star_power: number;
}

export const DEFAULT_WEIGHTS: WeightConfig = {
  vote_average: 0.25,
  vote_count: 0.15,
  popularity: 0.20,
  revenue: 0.10,
  runtime_quality: 0.05,
  release_recency: 0.10,
  cast_star_power: 0.15,
};
