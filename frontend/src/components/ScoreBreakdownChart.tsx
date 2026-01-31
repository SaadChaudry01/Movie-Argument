import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import type { ScoreBreakdown, RadarDataPoint, BarDataPoint } from '../types';

interface ScoreRadarProps {
  breakdown: ScoreBreakdown;
}

export function ScoreRadar({ breakdown }: ScoreRadarProps) {
  const data = breakdown.features.map((f) => ({
    feature: f.display_name,
    score: f.normalized_value,
    fullMark: 100,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="feature"
          tick={{ fill: '#9CA3AF', fontSize: 11 }}
        />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fill: '#6B7280', fontSize: 10 }}
        />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#f5a623"
          fill="#f5a623"
          fillOpacity={0.3}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

interface ComparisonRadarProps {
  data: RadarDataPoint[];
  movie1Title: string;
  movie2Title: string;
}

export function ComparisonRadar({ data, movie1Title, movie2Title }: ComparisonRadarProps) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <RadarChart cx="50%" cy="50%" outerRadius="65%" data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis
          dataKey="feature"
          tick={{ fill: '#9CA3AF', fontSize: 11 }}
        />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fill: '#6B7280', fontSize: 10 }}
        />
        <Radar
          name={movie1Title}
          dataKey="movie1"
          stroke="#f5a623"
          fill="#f5a623"
          fillOpacity={0.3}
          strokeWidth={2}
        />
        <Radar
          name={movie2Title}
          dataKey="movie2"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.3}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

interface ComparisonBarProps {
  data: BarDataPoint[];
  movie1Title: string;
  movie2Title: string;
}

export function ComparisonBar({ data, movie1Title, movie2Title }: ComparisonBarProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
      >
        <XAxis type="number" domain={[0, 100]} tick={{ fill: '#9CA3AF' }} />
        <YAxis
          type="category"
          dataKey="feature"
          tick={{ fill: '#9CA3AF', fontSize: 11 }}
          width={75}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1a1b23',
            border: '1px solid #374151',
            borderRadius: '8px',
          }}
          labelStyle={{ color: '#fff' }}
        />
        <Bar dataKey="movie1_score" name={movie1Title} fill="#f5a623" radius={[0, 4, 4, 0]} />
        <Bar dataKey="movie2_score" name={movie2Title} fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface FeatureBreakdownProps {
  breakdown: ScoreBreakdown;
}

export function FeatureBreakdown({ breakdown }: FeatureBreakdownProps) {
  return (
    <div className="space-y-3">
      {breakdown.features.map((feature) => (
        <div key={feature.name} className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-gray-300">{feature.display_name}</span>
            <span className="text-gray-400">
              {feature.normalized_value.toFixed(0)}/100
            </span>
          </div>
          <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full transition-all duration-500"
              style={{ width: `${feature.normalized_value}%` }}
            />
          </div>
          <p className="text-xs text-gray-500">{feature.explanation}</p>
        </div>
      ))}
    </div>
  );
}

interface ScoreGaugeProps {
  score: number;
  grade: string;
  size?: 'sm' | 'md' | 'lg';
}

export function ScoreGauge({ score, grade, size = 'md' }: ScoreGaugeProps) {
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-28 h-28',
    lg: 'w-36 h-36',
  };
  
  const textSizes = {
    sm: 'text-lg',
    md: 'text-2xl',
    lg: 'text-3xl',
  };
  
  const gradeSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`relative ${sizeClasses[size]}`}>
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke="#1f2937"
          strokeWidth="8"
          fill="none"
        />
        <circle
          cx="50%"
          cy="50%"
          r="45%"
          stroke={getScoreColor(score)}
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          style={{
            strokeDasharray: circumference,
            strokeDashoffset,
            transition: 'stroke-dashoffset 1s ease-out',
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold text-white ${textSizes[size]}`}>
          {score.toFixed(0)}
        </span>
        <span className={`font-semibold ${gradeSizes[size]} ${getGradeColorClass(grade)}`}>
          {grade}
        </span>
      </div>
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#f59e0b';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function getGradeColorClass(grade: string): string {
  if (grade.startsWith('A')) return 'text-emerald-400';
  if (grade.startsWith('B')) return 'text-yellow-400';
  if (grade.startsWith('C')) return 'text-orange-400';
  return 'text-red-400';
}
