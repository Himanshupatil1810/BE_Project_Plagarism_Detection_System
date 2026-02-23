export default function CircularScore({ score, size = 140 }) {
  const r = (size - 20) / 2
  const circ = 2 * Math.PI * r
  const fill = (score / 100) * circ
  const color =
    score > 70 ? 'var(--danger)' : score > 40 ? 'var(--warn)' : 'var(--accent)'

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="var(--bg3)" strokeWidth="8"
        />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circ}
          strokeDashoffset={circ - fill}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="absolute text-center">
        <div
          className="font-syne font-extrabold leading-none"
          style={{ fontSize: size * 0.25, color }}
        >
          {score}%
        </div>
        <div className="text-app3 font-jetbrains mt-1" style={{ fontSize: 11 }}>
          Similarity
        </div>
      </div>
    </div>
  )
}
