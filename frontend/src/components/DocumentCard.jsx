import React, { useState } from 'react'
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react'
import StatusBadge from './StatusBadge'

export default function DocumentCard({ document: doc, classification, required = false, className = '' }) {
  const [expanded, setExpanded] = useState(false)

  const displayName = classification?.classified_as || doc.document_type || doc.file_name

  return (
    <div className={`rounded-lg border border-border bg-white p-4 shadow-sm transition-shadow hover:shadow-md ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <button
          onClick={() => setExpanded(!expanded)}
          className="min-w-0 flex-1 text-left"
          aria-label={`Document: ${doc.file_name}`}
          type="button"
        >
          <div className="flex items-center gap-2">
            <h4 className="truncate text-sm font-medium text-foreground">
              {displayName}
            </h4>
            {required && (
              <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                Required
              </span>
            )}
          </div>
          {classification && (
            <p className="mt-1 text-xs text-muted-foreground">
              {doc.file_name}
            </p>
          )}
        </button>
        <div className="flex items-center gap-2 shrink-0">
          <StatusBadge status={doc.status} />
          <button
            onClick={() => setExpanded(!expanded)}
            className="rounded p-0.5 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label={expanded ? 'Collapse details' : 'Expand details'}
            type="button"
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {expanded && classification && (
        <div className="mt-3 space-y-3">
          {/* Classification Confidence */}
          <div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Classification Confidence</span>
              <span>{(classification.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  classification.confidence >= 0.8
                    ? 'bg-emerald-500'
                    : classification.confidence >= 0.5
                    ? 'bg-amber-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${classification.confidence * 100}%` }}
              />
            </div>
          </div>

          {/* Issues */}
          {classification.issues && classification.issues.length > 0 && (
            <div>
              <div className="flex items-center gap-1 text-xs font-medium text-red-600 mb-1">
                <AlertCircle size={12} />
                <span>{classification.issues.length} issue{classification.issues.length > 1 ? 's' : ''}</span>
              </div>
              <ul className="space-y-0.5">
                {classification.issues.map((issue, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-xs text-red-600">
                    <span className="mt-0.5 shrink-0">•</span>
                    <span>{issue.message || issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}