import React from 'react'

export default function ScoreCircle({ score, size = 80, label = '', className = '' }) {
  const radius = 42
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score))
  const offset = circumference - (clamped / 100) * circumference

  const getColor = (s) => {
    if (s >= 80) return 'stroke-emerald-500'
    if (s >= 60) return 'stroke-amber-500'
    return 'stroke-red-500'
  }

  const getTextColor = (s) => {
    if (s >= 80) return 'text-emerald-600'
    if (s >= 60) return 'text-amber-600'
    return 'text-red-600'
  }

  const autoLabel = clamped >= 80 ? 'Excellent' : clamped >= 60 ? 'Good' : 'Poor'

  return (
    <div className={`inline-flex flex-col items-center gap-1 ${className}`}>
      <svg width={size} height={size} viewBox="0 0 100 100" className="-rotate-90" role="img" aria-label={`Score: ${clamped}`}>
        {/* Background circle */}
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-gray-200"
        />
        {/* Foreground arc */}
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={`${getColor(clamped)} transition-all duration-700 ease-out`}
        />
      </svg>
      <span className={`text-xl font-bold ${getTextColor(clamped)}`}>
        {clamped}
      </span>
      <span className="text-xs text-gray-500">{label || autoLabel}</span>
    </div>
  )
}