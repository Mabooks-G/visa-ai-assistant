import React from 'react'

const statusStyles = {
  pending: 'bg-amber-100 text-amber-800 border-amber-300',
  processing: 'bg-blue-100 text-blue-800 border-blue-300',
  verified: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  failed: 'bg-red-100 text-red-800 border-red-300',
  needs_review: 'bg-orange-100 text-orange-800 border-orange-300',
  in_progress: 'bg-sky-100 text-sky-800 border-sky-300',
}

const statusLabels = {
  pending: 'Pending',
  processing: 'Processing',
  verified: 'Verified',
  rejected: 'Rejected',
  failed: 'Failed',
  needs_review: 'Needs Review',
  in_progress: 'In Progress',
}

export default function StatusBadge({ status, className = '' }) {
  const style = statusStyles[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  const label = statusLabels[status] || status

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${style} ${className}`}
    >
      <span
        className={`inline-block h-1.5 w-1.5 rounded-full ${
          status === 'verified' ? 'bg-emerald-500' :
          status === 'rejected' ? 'bg-red-500' :
          status === 'processing' ? 'bg-blue-500 animate-pulse' :
          status === 'needs_review' || status === 'in_progress' ? 'bg-amber-500' :
          'bg-gray-400'
        }`}
        aria-hidden="true"
      />
      {label}
    </span>
  )
}