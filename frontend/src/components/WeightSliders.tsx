import { useState } from 'react';
import { ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { WeightConfig } from '../types';
import { DEFAULT_WEIGHTS } from '../types';

interface WeightSlidersProps {
  weights: WeightConfig;
  onChange: (weights: WeightConfig) => void;
}

const WEIGHT_LABELS: Record<keyof WeightConfig, { label: string; description: string }> = {
  vote_average: {
    label: 'User Rating',
    description: 'TMDB user ratings (0-10 scale)',
  },
  vote_count: {
    label: 'Rating Confidence',
    description: 'Number of votes - more votes = more reliable',
  },
  popularity: {
    label: 'Popularity',
    description: 'TMDB popularity index - cultural impact',
  },
  revenue: {
    label: 'Box Office',
    description: 'Financial performance and profitability',
  },
  runtime_quality: {
    label: 'Runtime Quality',
    description: 'Optimal movie length (90-150 min ideal)',
  },
  release_recency: {
    label: 'Era Score',
    description: 'Classic status vs recency',
  },
  cast_star_power: {
    label: 'Star Power',
    description: 'Lead actor popularity and recognition',
  },
};

export default function WeightSliders({ weights, onChange }: WeightSlidersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleWeightChange = (key: keyof WeightConfig, value: number) => {
    onChange({
      ...weights,
      [key]: value,
    });
  };

  const handleReset = () => {
    onChange(DEFAULT_WEIGHTS);
  };

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);

  return (
    <div className="card p-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left"
      >
        <div>
          <h3 className="font-semibold text-white">Scoring Weights</h3>
          <p className="text-sm text-gray-500">
            Customize how movies are scored
          </p>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="pt-4 space-y-4">
              {(Object.keys(WEIGHT_LABELS) as Array<keyof WeightConfig>).map((key) => (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <label className="text-gray-300">
                      {WEIGHT_LABELS[key].label}
                    </label>
                    <span className="text-primary-400 font-medium">
                      {(weights[key] * 100).toFixed(0)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={weights[key]}
                    onChange={(e) => handleWeightChange(key, parseFloat(e.target.value))}
                    className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer
                             [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 
                             [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-primary-500 
                             [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:cursor-pointer
                             [&::-webkit-slider-thumb]:hover:bg-primary-400"
                  />
                  <p className="text-xs text-gray-600">
                    {WEIGHT_LABELS[key].description}
                  </p>
                </div>
              ))}

              <div className="flex items-center justify-between pt-2 border-t border-dark-700">
                <div className="text-sm">
                  <span className="text-gray-500">Total: </span>
                  <span className={totalWeight > 0 ? 'text-primary-400' : 'text-red-400'}>
                    {(totalWeight * 100).toFixed(0)}%
                  </span>
                  <span className="text-gray-600 text-xs ml-2">
                    (will be normalized)
                  </span>
                </div>
                <button
                  onClick={handleReset}
                  className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
