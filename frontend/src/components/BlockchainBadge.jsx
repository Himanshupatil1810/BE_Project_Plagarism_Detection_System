import { Shield, Hash, Database, Layers, CheckCircle } from 'lucide-react'
import { CopyButton } from './Badges.jsx'

export default function BlockchainBadge({ data }) {
  if (!data) return null

  const rows = [
    { label: 'Transaction Hash', key: 'transaction_hash', Icon: Hash },
    { label: 'IPFS CID',         key: 'ipfs_cid',         Icon: Database },
    { label: 'Block Number',     key: 'block_number',     Icon: Layers },
  ].filter((r) => data[r.key])

  return (
    <div className="blockchain-card">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div
          className="flex items-center justify-center rounded-xl flex-shrink-0"
          style={{ width: 40, height: 40, background: 'var(--accent-dim)' }}
        >
          <Shield size={18} color="var(--accent)" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-syne font-bold text-app" style={{ fontSize: 15 }}>
            Blockchain Verified
          </div>
          <div className="text-app3 font-jetbrains" style={{ fontSize: 11 }}>
            Immutably stored on-chain
          </div>
        </div>
        <span className="badge badge-verified">
          <CheckCircle size={10} />
          Verified
        </span>
      </div>

      {/* Rows */}
      {rows.map(({ label, key, Icon }) => (
        <div key={key} className="flex items-start gap-3 mb-4 last:mb-0">
          <div
            className="flex items-center justify-center rounded-lg flex-shrink-0 mt-0.5"
            style={{ width: 30, height: 30, background: 'var(--accent-dim)' }}
          >
            <Icon size={13} color="var(--accent)" />
          </div>
          <div className="flex-1 min-w-0">
            <div
              className="font-jetbrains text-app3 uppercase mb-0.5"
              style={{ fontSize: 10, letterSpacing: '0.5px' }}
            >
              {label}
            </div>
            <div
              className="font-jetbrains text-app break-all flex items-start"
              style={{ fontSize: 12 }}
            >
              <span className="flex-1">{String(data[key])}</span>
              <CopyButton text={String(data[key])} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
