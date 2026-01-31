/**
 * Utility functions for formatting data in the UI.
 */

/**
 * Format a number as currency (USD).
 */
export function formatCurrency(value: number): string {
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(0)}M`;
  }
  if (value >= 1_000) {
    return `$${(value / 1_000).toFixed(0)}K`;
  }
  return `$${value}`;
}

/**
 * Format a large number with abbreviation.
 */
export function formatNumber(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toLocaleString();
}

/**
 * Format runtime in hours and minutes.
 */
export function formatRuntime(minutes: number | null): string {
  if (!minutes) return 'N/A';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

/**
 * Format a date string to year only.
 */
export function formatYear(dateString: string | null): string {
  if (!dateString) return 'N/A';
  try {
    return dateString.split('-')[0];
  } catch {
    return 'N/A';
  }
}

/**
 * Format a date string to full date.
 */
export function formatDate(dateString: string | null): string {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return 'N/A';
  }
}

/**
 * Get grade color class based on letter grade.
 */
export function getGradeColor(grade: string): string {
  const letter = grade.charAt(0).toUpperCase();
  switch (letter) {
    case 'A':
      return 'text-emerald-400';
    case 'B':
      return 'text-yellow-400';
    case 'C':
      return 'text-orange-400';
    case 'D':
      return 'text-red-400';
    case 'F':
      return 'text-red-500';
    default:
      return 'text-gray-400';
  }
}

/**
 * Get grade background color class.
 */
export function getGradeBgColor(grade: string): string {
  const letter = grade.charAt(0).toUpperCase();
  switch (letter) {
    case 'A':
      return 'bg-emerald-500/20';
    case 'B':
      return 'bg-yellow-500/20';
    case 'C':
      return 'bg-orange-500/20';
    case 'D':
      return 'bg-red-500/20';
    case 'F':
      return 'bg-red-600/20';
    default:
      return 'bg-gray-500/20';
  }
}

/**
 * Get score color based on numeric value.
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'; // emerald
  if (score >= 60) return '#f59e0b'; // amber
  if (score >= 40) return '#f97316'; // orange
  return '#ef4444'; // red
}

/**
 * Calculate ROI percentage.
 */
export function calculateROI(revenue: number, budget: number): string {
  if (budget <= 0) return 'N/A';
  const roi = ((revenue - budget) / budget) * 100;
  const sign = roi >= 0 ? '+' : '';
  return `${sign}${roi.toFixed(0)}%`;
}

/**
 * Truncate text with ellipsis.
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

/**
 * Get confidence level description.
 */
export function getConfidenceDescription(confidence: string): string {
  switch (confidence) {
    case 'decisive':
      return 'Clear winner with significant margin';
    case 'clear':
      return 'Definite winner with good margin';
    case 'close':
      return 'Close competition, slight edge';
    case 'very_close':
      return 'Extremely tight, nearly tied';
    default:
      return confidence;
  }
}
