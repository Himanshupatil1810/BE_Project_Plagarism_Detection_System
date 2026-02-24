import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart2, Clock, CheckCircle, AlertTriangle, Shield, Zap, FileText, X } from 'lucide-react'
import FileUpload from '../components/FileUpload.jsx'
import { useAuth } from '../context/AuthContext.jsx'
// Add getUserReports to the curly braces
import { checkPlagiarism, getUserReports } from '../api/plagiarismApi.js'

export default function Dashboard() {
  const { user } = useAuth()
  const navigate  = useNavigate()

  const [file,    setFile]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [stats,   setStats]   = useState({ total: 0, flagged: 0, clean: 0, onChain: 0 })

  useEffect(() => {
  const fetchDatabaseStats = async () => {
    try {
      // Ensure getUserReports is now imported so this line works
      const data = await getUserReports(user.user_id);
      const reports = data.reports || [];

      setStats({
        total: reports.length,
        // item.report[4] is overall_score
        flagged: reports.filter((item) => (item.report[4] || 0) > 0.4).length,
        // item.report[4] is overall_score
        clean: reports.filter((item) => (item.report[4] || 0) <= 0.4).length,
        // item.report[9] is blockchain_tx_hash
        onChain: reports.filter((item) => item.report[9]).length,
      });
    } catch (err) {
      console.error("Failed to fetch database stats:", err);
    }
  };

  if (user?.user_id) {
    fetchDatabaseStats();
  }
}, [user.user_id]);

  const handleCheck = async () => {
    if (!file) return
    setLoading(true)
    setError('')

    try {
      // 1. Get the data from Flask
      const apiResult = await checkPlagiarism(file, user.user_id)
      
      // 2. ADD THIS LOG HERE
      console.log("RAW FLASK RESPONSE:", apiResult)

      const result = {
        ...apiResult,
        // Explicitly normalize keys for the UI
        sources: apiResult.sources || [],
        sections: apiResult.sections || apiResult.plagiarized_sections || [],
        document_text: apiResult.document_text || apiResult.content || apiResult.text || '',
        overall_similarity_score: apiResult.overall_score || 0,
        blockchain_data: apiResult.blockchain_verification || {}
      };

      sessionStorage.setItem('chainguard_latest', JSON.stringify(result))
      navigate('/results')
    } catch (err) {
      console.error("Full Error Object:", err)
      setError(err?.message || 'Failed to analyze document.')
    } finally {
      setLoading(false)
    }
  }

  const STAT_CARDS = [
    { label: 'Total Checks', value: stats.total,   Icon: BarChart2,   color: 'var(--info-dim)',   iconColor: 'var(--info)'   },
    { label: 'Flagged',      value: stats.flagged,  Icon: AlertTriangle, color: 'var(--danger-dim)', iconColor: 'var(--danger)' },
    { label: 'Clean Docs',   value: stats.clean,    Icon: CheckCircle, color: 'var(--accent-dim)', iconColor: 'var(--accent)' },
    { label: 'On-Chain',     value: stats.onChain,  Icon: Shield,      color: 'var(--purple-dim)', iconColor: 'var(--purple)' },
  ]

  return (
    <div className="p-7 max-w-5xl fade-in">

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {STAT_CARDS.map(({ label, value, Icon, color, iconColor }) => (
          <div key={label} className="card">
            <div
              className="flex items-center justify-center rounded-xl mb-3"
              style={{ width: 38, height: 38, background: color }}
            >
              <Icon size={17} color={iconColor} />
            </div>
            <div className="font-syne font-extrabold text-app leading-none" style={{ fontSize: 30 }}>
              {value}
            </div>
            <div className="font-jetbrains text-app3 mt-1" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.6px' }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      {/* Upload card */}
      <div className="card">
        <div className="flex items-start justify-between mb-5">
          <div>
            <h2 className="font-syne font-bold text-app" style={{ fontSize: 17 }}>
              Upload Document
            </h2>
            <p className="text-app2 mt-0.5 text-sm">
              AI-powered plagiarism check with permanent blockchain verification
            </p>
          </div>
        </div>

        <FileUpload file={file} onFile={setFile} onClear={() => setFile(null)} />

        {file && (
          <div className="mt-4">
            {/* Selected file row */}
            <div className="flex items-center gap-3">
              <div
                className="flex-1 flex items-center gap-2.5 px-4 py-3 rounded-lg"
                style={{ background: 'var(--bg3)', border: '1px solid var(--border)' }}
              >
                <FileText size={14} color="var(--accent)" />
                <span className="text-sm text-app font-medium truncate">{file.name}</span>
                <span className="badge badge-info ml-auto">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>

              <button
                className="btn btn-primary"
                onClick={handleCheck}
                disabled={loading}
                style={{ minWidth: 150 }}
              >
                {loading ? (
                  <><div className="spinner" />Analyzing…</>
                ) : (
                  <><Zap size={15} />Check Now</>
                )}
              </button>

              <button
                className="icon-btn"
                onClick={() => setFile(null)}
                title="Remove file"
              >
                <X size={14} />
              </button>
            </div>

            {/* Blockchain notice */}
            <div className="flex items-center gap-2 mt-2">
              <Shield size={12} color="var(--accent)" />
              <span className="text-app3" style={{ fontSize: 12 }}>
                Result will be permanently stored on blockchain for immutable verification
              </span>
            </div>
          </div>
        )}

        {error && (
          <div
            className="mt-4 text-danger text-sm rounded-lg px-3 py-2.5"
            style={{ background: 'var(--danger-dim)' }}
          >
            {error}
          </div>
        )}
      </div>

      {/* Quick tips */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {[
          { title: 'How it works',      body: 'Upload your document and our AI scans millions of sources for similarities.' },
          { title: 'Blockchain proof',  body: 'Every report is hashed and stored on-chain, creating an immutable audit trail.' },
          { title: 'Instant results',   body: 'Get a detailed similarity report with highlighted text within seconds.' },
        ].map(({ title, body }) => (
          <div key={title} className="card card-sm">
            <div className="font-syne font-bold text-app mb-1.5" style={{ fontSize: 14 }}>{title}</div>
            <div className="text-app2" style={{ fontSize: 13 }}>{body}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
