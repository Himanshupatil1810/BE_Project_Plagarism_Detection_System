import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, CheckCircle, AlertTriangle, XCircle,
  Hash, Shield, Download
} from 'lucide-react'
import CircularScore     from '../components/CircularScore.jsx'
import BlockchainBadge  from '../components/BlockchainBadge.jsx'
import SourceList        from '../components/SourceList.jsx'
import DocumentViewer    from '../components/DocumentViewer.jsx'
import { RiskBadge, CopyButton } from '../components/Badges.jsx'
import { getDownloadUrl }  from '../api/plagiarismApi.js'

const TABS = ['overview', 'sources', 'document', 'blockchain']

export default function ReportDetails() {
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [tab,    setTab]    = useState('overview')

  useEffect(() => {
    const raw = sessionStorage.getItem('chainguard_latest')
    if (raw) { 
      try { 
        const parsed = JSON.parse(raw);
        console.log("Loaded Report:", parsed); // Always log this to see what's actually there
        setResult(parsed);
      } catch (e) {
        console.error("Failed to parse report data from session:", e);
      } 
    }
  }, [])

  if (!result) {
    return (
      <div className="p-7">
        <button className="btn btn-ghost btn-sm mb-6" onClick={() => navigate('/')}>
          <ArrowLeft size={14} /> Back to Dashboard
        </button>
        <div className="card text-center py-16">
          <div className="font-syne font-bold text-app mb-2" style={{ fontSize: 18 }}>
            No Result to Display
          </div>
          <p className="text-app2 text-sm mb-6">Upload a document first to see results here.</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Upload a Document
          </button>
        </div>
      </div>
    )
  }

  const score    = Math.round((result.overall_similarity_score || result.overall_score || 0) * 100);
  const risk       = score > 70 ? 'High' : score > 40 ? 'Medium' : 'Low'
  const sources = result.sources || [];
  const sections = result.sections || result.plagiarized_sections || [];
  const docText = result.document_text || result.content || result.text || "";
  const blockchain = result.blockchain_data || result.blockchain
  const reportId   = result.report_id || result.id || ''

  return (
    <div className="p-7 max-w-5xl fade-in">
      {/* Page header */}
      <div className="flex items-center gap-3 mb-6">
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/')}>
          <ArrowLeft size={14} /> Back
        </button>
        <div className="flex-1 min-w-0">
          <h2 className="font-syne font-bold text-app" style={{ fontSize: 20 }}>
            Analysis Results
          </h2>
          <div className="font-jetbrains text-app3 truncate mt-0.5" style={{ fontSize: 11 }}>
            {reportId}
          </div>
        </div>
        <RiskBadge level={risk} />
        {reportId && (
          <a
            href={getDownloadUrl(reportId)}
            download
            className="btn btn-ghost btn-sm"
          >
            <Download size={14} /> Download JSON
          </a>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5" style={{ borderBottom: '1px solid var(--border)' }}>
        {TABS.map((t) => (
          <button
            key={t}
            className={`tab-btn ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Score card */}
          <div className="card">
            <div className="font-syne font-bold text-app mb-5" style={{ fontSize: 16 }}>
              Similarity Score
            </div>
            <div className="flex items-center gap-6 mb-5">
              <CircularScore score={score} />
              <div>
                <div className="font-syne font-extrabold text-app mb-1" style={{ fontSize: 22 }}>
                  {risk} Risk
                </div>
                <p className="text-app2 text-sm mb-3">
                  {score > 70
                    ? 'High plagiarism detected. Immediate review required.'
                    : score > 40
                    ? 'Moderate similarity found. Review flagged sections.'
                    : 'Low similarity. Document appears largely original.'}
                </p>
                <div className="font-jetbrains text-app3" style={{ fontSize: 11 }}>
                  {sources.length} source{sources.length !== 1 ? 's' : ''} matched
                </div>
              </div>
            </div>

            {/* Mini stats */}
            <div
              className="h-px w-full my-4"
              style={{ background: 'var(--border)' }}
            />
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Sources',  val: sources.length, color: 'var(--info)'   },
                { label: 'Sections', val: sections.length, color: 'var(--warn)'  },
                { label: 'Original', val: `${100 - score}%`, color: 'var(--accent)' },
              ].map(({ label, val, color }) => (
                <div
                  key={label}
                  className="text-center rounded-lg py-3"
                  style={{ background: 'var(--bg3)' }}
                >
                  <div className="font-syne font-extrabold" style={{ fontSize: 22, color }}>
                    {val}
                  </div>
                  <div className="text-app3" style={{ fontSize: 11 }}>{label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right column */}
          <div className="flex flex-col gap-4">
            {blockchain
              ? <BlockchainBadge data={blockchain} />
              : (
                <div className="card">
                  <div className="font-syne font-bold text-app mb-2" style={{ fontSize: 15 }}>
                    Blockchain Status
                  </div>
                  <p className="text-app2 text-sm">No blockchain data available for this report.</p>
                </div>
              )
            }

            {/* Report ID card */}
            <div className="card card-sm">
              <div className="font-syne font-bold text-app mb-3" style={{ fontSize: 14 }}>
                Report ID
              </div>
              <div
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg"
                style={{ background: 'var(--bg3)', border: '1px solid var(--border)' }}
              >
                <Hash size={13} color="var(--accent)" className="flex-shrink-0" />
                <span className="font-jetbrains text-app flex-1 break-all" style={{ fontSize: 11 }}>
                  {reportId || 'N/A'}
                </span>
                {reportId && <CopyButton text={reportId} />}
              </div>
              <p className="text-app3 mt-2" style={{ fontSize: 11 }}>
                Use this ID in the Verification Portal to confirm on-chain status.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Sources ── */}
      {tab === 'sources' && (
        <div className="card">
          <div className="font-syne font-bold text-app mb-4" style={{ fontSize: 16 }}>
            Matched Sources
          </div>
          <SourceList sources={sources} />
        </div>
      )}

      {/* ── Document ── */}
      {tab === 'document' && (
        <div className="card">
          <div className="mb-4">
            <div className="font-syne font-bold text-app mb-1" style={{ fontSize: 16 }}>
              Document Viewer
            </div>
            <p className="text-app2 text-sm">
              Highlighted text indicates potentially plagiarized sections.
            </p>
          </div>
          {/* Legend */}
          <div className="flex gap-4 mb-4 flex-wrap">
            {[
              ['hl-high',   'High Risk'],
              ['hl-medium', 'Medium Risk'],
              ['hl-low',    'Low Risk'],
            ].map(([cls, label]) => (
              <span key={cls} className={cls} style={{ padding: '2px 10px', borderRadius: 4, fontSize: 13 }}>
                {label}
              </span>
            ))}
          </div>
          <DocumentViewer text={docText} sections={sections} />
        </div>
      )}

      {/* ── Blockchain ── */}
      {tab === 'blockchain' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <BlockchainBadge data={blockchain || {}} />
          <div className="card">
            <div className="font-syne font-bold text-app mb-4" style={{ fontSize: 16 }}>
              Verification Details
            </div>
            {[
              { label: 'Report ID',  val: reportId },
              { label: 'Timestamp', val: result.timestamp },
              { label: 'User ID',   val: result.user_id },
              { label: 'Status',    val: result.status || 'completed' },
              { label: 'File',      val: result.filename || result._filename },
            ]
              .filter((r) => r.val)
              .map(({ label, val }) => (
                <div key={label} className="mb-4">
                  <div
                    className="font-jetbrains text-app3 uppercase mb-0.5"
                    style={{ fontSize: 10, letterSpacing: '0.5px' }}
                  >
                    {label}
                  </div>
                  <div className="flex items-center font-jetbrains text-app" style={{ fontSize: 12 }}>
                    <span className="flex-1 break-all">
                      {String(val).slice(0, 80)}{String(val).length > 80 ? '…' : ''}
                    </span>
                    <CopyButton text={String(val)} />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
