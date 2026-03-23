import { useState } from 'react'
import { Search, CheckCircle, XCircle, Shield, Hash, AlertTriangle } from 'lucide-react'
import { verifyReport } from '../api/plagiarismApi.js'
import { CopyButton } from '../components/Badges.jsx'

export default function Verify() {
  const [hash,    setHash]    = useState('')
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)
  const [error,   setError]   = useState('')
  const [file, setFile] = useState(null)
  const [integrityStatus, setIntegrityStatus] = useState(null) // 'Match' | 'Tampered' | null

  const verify = async () => {
    const h = hash.trim()
    if (!h) return
    setLoading(true); setError(''); setResult(null)
    setFile(null)
    setIntegrityStatus(null)
    try {
      const response = await verifyReport(h)
      
      // FIX: Map the nested blockchain_verification object to the result state
      if (response && response.blockchain_verification) {
        setResult({
          ...response.blockchain_verification,
          // Merge report_data fields if you want to show them too
          report_id: response.report_data ? response.report_data[1] : h,
          ipfs_hash: response.report_data ? response.report_data[10] : ''
        })
      } else {
        setError('Unexpected response format from server.')
      }
    } catch (err) {
      setError('Connection to verification server failed.')
      console.error(err)
    }
    setLoading(false)
  }

const LABEL_MAP = {
    report_id:        'Report ID',
    plagiarism_score: 'Similarity Score', // From your metadata object
    total_sources:    'Sources Scanned',   // From your metadata object
    timestamp:        'Anchored At',
    document_hash:    'Document Fingerprint',
    ipfs_hash:        'Verified Data Source (IPFS)',
  }

  const sha256Hex = async (arrayBuffer) => {
    const subtle = window.crypto?.subtle
    if (!subtle) throw new Error('WebCrypto is not available in this browser context.')
    const digestBuffer = await subtle.digest('SHA-256', arrayBuffer)
    const bytes = new Uint8Array(digestBuffer)
    return Array.from(bytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('')
  }

  const handleIntegrityFile = async (selectedFile) => {
    if (!selectedFile) return
    setFile(selectedFile)
    setIntegrityStatus(null)

    try {
      const buf = await selectedFile.arrayBuffer()
      const computedHash = await sha256Hex(buf)
      const expectedHash = String(result?.document_hash || '').toLowerCase()
      const actualHash = String(computedHash || '').toLowerCase()

      setIntegrityStatus(actualHash && expectedHash && actualHash === expectedHash ? 'Match' : 'Tampered')
    } catch (e) {
      console.error(e)
      setError('Could not compute SHA-256 hash for integrity check in this browser.')
      setIntegrityStatus(null)
    }
  }

  return (
    <div className="p-7 max-w-2xl fade-in">
      <div className="card">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-syne font-bold text-app" style={{ fontSize: 17 }}>
              Verification Portal
            </h2>
            <p className="text-app2 mt-0.5 text-sm">
              Enter a Report ID to confirm its blockchain status
            </p>
          </div>
          <div
            className="flex items-center justify-center rounded-xl"
            style={{ width: 44, height: 44, background: 'var(--accent-dim)' }}
          >
            <Search size={20} color="var(--accent)" />
          </div>
        </div>

        {/* Input row */}
        <div className="flex gap-3">
          <input
            className="form-input flex-1"
            placeholder="Enter Report ID — e.g. PLAG_1715000000000_AB1C2D"
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && verify()}
          />
          <button
            className="btn btn-primary"
            onClick={verify}
            disabled={loading || !hash.trim()}
            style={{ minWidth: 110 }}
          >
            {loading ? <div className="spinner" /> : <><Search size={14} />Verify</>}
          </button>
        </div>

        <p className="text-app3 mt-2" style={{ fontSize: 12 }}>
          <Hash size={11} style={{ display: 'inline', marginRight: 4 }} />
          Copy the Report ID from your results page or report history.
        </p>

        {error && (
          <div
            className="mt-4 text-danger text-sm rounded-lg px-3 py-2.5"
            style={{ background: 'var(--danger-dim)' }}
          >
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-5 fade-in">
            <div className="h-px w-full mb-5" style={{ background: 'var(--border)' }} />

            {/* Status banner */}
            <div className="flex items-center gap-3 mb-5">
              {result.verified ? (
                <>
                  <CheckCircle size={20} color="var(--accent)" />
                  <div className="flex-1">
                    <div className="font-syne font-bold text-app" style={{ fontSize: 16 }}>
                      Verification Successful
                    </div>
                    <div className="text-app2 text-sm">This document is registered on-chain.</div>
                  </div>
                  <span className="badge badge-verified">
                    <Shield size={10} /> On-Chain
                  </span>
                </>
              ) : (
                <>
                  <XCircle size={20} color="var(--danger)" />
                  <div className="flex-1">
                    <div className="font-syne font-bold text-app" style={{ fontSize: 16 }}>
                      Not Found On-Chain
                    </div>
                    <div className="text-app2 text-sm">
                      This report hash was not found in the blockchain registry.
                    </div>
                  </div>
                  <span className="badge badge-high">Unverified</span>
                </>
              )}
            </div>

            {/* Metadata rows */}
            {(
              (() => {
                const meta = result.metadata || {}
                const entries = Object.entries(meta)
                if (result.document_hash) entries.push(['document_hash', result.document_hash])
                if (result.ipfs_hash) entries.push(['ipfs_hash', result.ipfs_hash])
                return entries
              })()
            ).map(([key, val]) => (
              <div key={key} className="flex gap-4 py-3" style={{ borderBottom: '1px solid var(--border)' }}>
                <div
                  className="font-jetbrains text-app3 uppercase flex-shrink-0"
                  style={{ fontSize: 10, letterSpacing: '0.5px', minWidth: 130, paddingTop: 2 }}
                >
                  {LABEL_MAP[key] || key.replace(/_/g, ' ')}
                </div>
                <div className="font-jetbrains text-app break-all" style={{ fontSize: 12 }}>
                  {key === 'ipfs_hash' ? (
                    <>
                      <a
                        href={`http://127.0.0.1:8080/ipfs/${String(val)}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: 'inherit', textDecoration: 'underline' }}
                        title="Open via local IPFS gateway"
                      >
                        {String(val)}
                      </a>
                      <CopyButton text={String(val)} />
                    </>
                  ) : (
                    String(val)
                  )}
                </div>
              </div>
            ))}

            {result.ipfs_hash && (
              <div className="text-app3 mt-3" style={{ fontSize: 11 }}>
                Note: This CID serves as the decentralized immutable address for this specific report's metadata.
              </div>
            )}

            {/* Integrity check upload (only after successful blockchain lookup) */}
            {result.verified && (
              <div className="mt-5">
                <div className="font-syne font-bold text-app mb-3" style={{ fontSize: 14 }}>
                  Upload Document for Integrity Check
                </div>

                <input
                  type="file"
                  className="form-input"
                  onChange={(e) => handleIntegrityFile(e.target.files?.[0] || null)}
                  style={{
                    background: 'var(--bg3)',
                    border: '1px solid var(--border)',
                    borderRadius: 10,
                  }}
                />

                {file && (
                  <div className="text-app3 mt-2" style={{ fontSize: 11 }}>
                    Selected: <span className="font-jetbrains">{file.name}</span>
                  </div>
                )}

                {integrityStatus && (
                  <div
                    className="mt-4 flex items-center gap-3"
                    style={{
                      color: integrityStatus === 'Match' ? 'var(--accent)' : 'var(--danger)',
                    }}
                  >
                    {integrityStatus === 'Match' ? (
                      <>
                        <Shield size={18} color="var(--accent)" />
                        <div className="font-syne font-bold text-app" style={{ fontSize: 14 }}>
                          Integrity Verified
                        </div>
                      </>
                    ) : (
                      <>
                        <AlertTriangle size={18} color="var(--danger)" />
                        <div className="font-syne font-bold text-app" style={{ fontSize: 14 }}>
                          Document Modified
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Info card */}
      <div className="card card-sm mt-4">
        <div className="font-syne font-bold text-app mb-2" style={{ fontSize: 14 }}>
          How Verification Works
        </div>
        <p className="text-app2 text-sm">
          When you run a plagiarism check, the result is hashed and stored permanently
          on the blockchain. The <strong>Report ID</strong> serves as the lookup key.
          Anyone with the Report ID can independently verify the document was checked
          at a specific time and that the results haven't been tampered with.
        </p>
      </div>
    </div>
  )
}
