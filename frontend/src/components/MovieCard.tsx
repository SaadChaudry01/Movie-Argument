import { Link } from 'react-router-dom';
import { Star, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import type { MovieBasic } from '../types';
import { getPosterUrl } from '../services/api';

interface MovieCardProps {
  movie: MovieBasic;
  score?: number;
  grade?: string;
  onClick?: () => void;
  selected?: boolean;
  showLink?: boolean;
}

export default function MovieCard({
  movie,
  score,
  grade,
  onClick,
  selected,
  showLink = true,
}: MovieCardProps) {
  const year = movie.release_date ? movie.release_date.split('-')[0] : 'N/A';
  
  const content = (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`card overflow-hidden cursor-pointer transition-all ${
        selected ? 'ring-2 ring-primary-500' : 'hover:border-dark-500'
      }`}
      onClick={onClick}
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-dark-800">
        <img
          src={getPosterUrl(movie.poster_path)}
          alt={movie.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        
        {/* Rating badge */}
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-dark-900/90 backdrop-blur-sm px-2 py-1 rounded-md">
          <Star className="w-3.5 h-3.5 text-primary-500 fill-primary-500" />
          <span className="text-sm font-semibold text-white">
            {movie.vote_average.toFixed(1)}
          </span>
        </div>

        {/* Score badge if available */}
        {score !== undefined && grade && (
          <div className="absolute top-2 left-2 bg-dark-900/90 backdrop-blur-sm px-2 py-1 rounded-md">
            <span className={`text-sm font-bold ${getGradeColor(grade)}`}>
              {grade}
            </span>
          </div>
        )}
        
        {/* Selected indicator */}
        {selected && (
          <div className="absolute inset-0 bg-primary-500/20 flex items-center justify-center">
            <div className="bg-primary-500 text-dark-950 px-3 py-1 rounded-full font-bold text-sm">
              Selected
            </div>
          </div>
        )}
      </div>

      <div className="p-3">
        <h3 className="font-semibold text-white text-sm line-clamp-2 mb-1">
          {movie.title}
        </h3>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Calendar className="w-3 h-3" />
          <span>{year}</span>
          {score !== undefined && (
            <>
              <span className="text-gray-600">•</span>
              <span className="text-primary-400">{score.toFixed(1)} pts</span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );

  if (showLink && !onClick) {
    return <Link to={`/movie/${movie.id}`}>{content}</Link>;
  }

  return content;
}

function getGradeColor(grade: string): string {
  if (grade.startsWith('A')) return 'text-emerald-400';
  if (grade.startsWith('B')) return 'text-yellow-400';
  if (grade.startsWith('C')) return 'text-orange-400';
  if (grade.startsWith('D')) return 'text-red-400';
  return 'text-red-500';
}
