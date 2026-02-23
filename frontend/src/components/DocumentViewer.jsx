export default function DocumentViewer({ text = '', sections = [] }) {
  if (!text) {
    return (
      <div className="doc-viewer text-app2 text-sm">
        No document text available to display.
      </div>
    )
  }

  // Build highlighted segments from plagiarized_sections
  const sorted = [...sections].sort(
    (a, b) => (a.start_char || 0) - (b.start_char || 0)
  )

  const segments = []
  let pos = 0

  sorted.forEach((sec) => {
    const start = sec.start_char ?? 0
    const end   = sec.end_char   ?? start + (sec.text?.length || 60)

    if (start > pos) {
      segments.push({ content: text.slice(pos, start), type: 'normal' })
    }

    const hlClass =
      sec.risk === 'High'
        ? 'hl-high'
        : sec.risk === 'Medium'
        ? 'hl-medium'
        : 'hl-low'

    segments.push({
      content: text.slice(start, end) || sec.text || '',
      type: hlClass,
      title: sec.source ? `Source: ${sec.source}` : 'Plagiarized section',
    })
    pos = end
  })

  if (pos < text.length) {
    segments.push({ content: text.slice(pos), type: 'normal' })
  }

  return (
    <div className="doc-viewer">
      {segments.map((seg, i) =>
        seg.type === 'normal' ? (
          <span key={i}>{seg.content}</span>
        ) : (
          <span key={i} className={seg.type} title={seg.title}>
            {seg.content}
          </span>
        )
      )}
    </div>
  )
}
