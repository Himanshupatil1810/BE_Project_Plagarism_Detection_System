import { Globe } from 'lucide-react'
import { RiskBadge } from './Badges.jsx'

export default function SourceList({ sources = [] }) {
  if (!sources.length) {
    return (
      <div className="text-center py-12">
        <div className="font-syne font-bold text-app mb-1">No Sources Found</div>
        <div className="text-app2 text-sm">No significant plagiarism sources were detected.</div>
      </div>
    )
  }

  return (
    <div>
      {sources.map((s, i) => {
        const sim = Math.round((s.similarity || s.similarity_score || 0) * 100)
        const risk = sim > 70 ? 'High' : sim > 40 ? 'Medium' : 'Low'
        const fillColor =
          risk === 'High' ? 'var(--danger)' : risk === 'Medium' ? 'var(--warn)' : 'var(--accent2)'

        return (
          <div className="source-item" key={i}>
            {/* URL row */}
            <div className="flex items-center gap-2 mb-2">
              <Globe size={13} color="var(--info)" className="flex-shrink-0" />
              <span
                className="font-jetbrains truncate"
                style={{ fontSize: 12, color: 'var(--info)' }}
              >
                {s.url || s.source || `Source ${i + 1}`}
              </span>
            </div>

            {/* Similarity bar */}
            <div className="flex items-center gap-3">
              <div className="sim-bar">
                <div
                  className="sim-fill"
                  style={{ width: `${sim}%`, background: fillColor }}
                />
              </div>
              <span
                className="font-jetbrains font-bold flex-shrink-0"
                style={{ fontSize: 13, color: fillColor, minWidth: 36 }}
              >
                {sim}%
              </span>
              <RiskBadge level={risk} />
            </div>

            {/* Matched text */}
            {(s.matched_text || s.excerpt) && (
              <div
                className="mt-2 text-app2"
                style={{
                  fontSize: 13,
                  fontFamily: 'Georgia, serif',
                  borderLeft: `3px solid ${fillColor}`,
                  paddingLeft: 10,
                }}
              >
                "
                {(s.matched_text || s.excerpt).slice(0, 150)}
                {(s.matched_text || s.excerpt).length > 150 ? '…' : ''}
                "
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
