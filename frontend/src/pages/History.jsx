import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, RefreshCw, Eye, Download, CheckCircle, Shield } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { getUserReports, getDownloadUrl } from '../api/plagiarismApi.js'
import { loadHistory } from '../utils/mockData.js'
import { RiskBadge } from '../components/Badges.jsx'

export default function History() {
  const { user }   = useAuth()
  const navigate   = useNavigate()
  const [reports,    setReports]    = useState([])
  const [loading,    setLoading]    = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchReports = async (showRefresh = false) => {
  if (showRefresh) setRefreshing(true)
  try {
    const data = await getUserReports(user.user_id)
    
    // Access the 'reports' key from your console output
    const backendReports = data.reports || []

    // Map the nested objects into a flat structure the table expects
    const formattedReports = backendReports.map(item => ({
      // Data from the 'submission' part
      id: item.submission[0],
      filename: item.submission[1],
      user_id: item.submission[4],
      status: item.submission[6],
      timestamp: item.submission[7],
      
      // Data from the 'report' part
      report_id: item.report[1],
      overall_similarity_score: item.report[4],
      blockchain_data: item.report[9],
      ipfs_hash: item.report[10]
    }))

    setReports(formattedReports)
  } catch (error) {
    console.error("Fetch error:", error)
    setReports(loadHistory(user.user_id))
  }
  setLoading(false)
  setRefreshing(false)
  }

  useEffect(() => { fetchReports() }, [user.user_id])

  const viewReport = (r) => {
    sessionStorage.setItem('chainguard_latest', JSON.stringify(r))
    navigate('/results')
  }

  if (loading) {
    return (
      <div className="p-7 flex justify-center items-center" style={{ minHeight: 300 }}>
        <div className="spinner spinner-lg" style={{ color: 'var(--accent)' }} />
      </div>
    )
  }

  return (
    <div className="p-7 max-w-5xl fade-in">
      <div className="card">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="font-syne font-bold text-app" style={{ fontSize: 17 }}>
              Report History
            </h2>
            <p className="text-app2 mt-0.5 text-sm">
              {reports.length} check{reports.length !== 1 ? 's' : ''} performed
            </p>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => fetchReports(true)}
            disabled={refreshing}
          >
            <RefreshCw
              size={13}
              style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }}
            />
            Refresh
          </button>
        </div>

        {/* Empty state */}
        {reports.length === 0 ? (
          <div className="text-center py-16">
            <div
              className="flex items-center justify-center rounded-2xl mx-auto mb-4"
              style={{ width: 56, height: 56, background: 'var(--bg3)' }}
            >
              <Clock size={24} color="var(--text3)" />
            </div>
            <div className="font-syne font-bold text-app mb-1.5" style={{ fontSize: 17 }}>
              No History Yet
            </div>
            <p className="text-app2 text-sm mb-5">
              Upload a document to start building your report history.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              Upload a Document
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="hist-table">
              <thead>
                <tr>
                  <th>Report ID</th>
                  <th>File</th>
                  <th>Date</th>
                  <th>Score</th>
                  <th>Risk</th>
                  <th>Blockchain</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r, i) => {
                  const score = Math.round((r.overall_similarity_score || 0) * 100)
                  const risk = score > 70 ? 'High' : score > 40 ? 'Medium' : 'Low'
                  const rId = r.report_id

                  return (
                    <tr key={i}>
                      <td>{rId.slice(0, 15)}...</td>
                      <td>{r.filename}</td>
                      <td>{new Date(r.timestamp).toLocaleDateString()}</td>
                      <td>{score}%</td>
                      <td><RiskBadge level={risk} /></td>
                      <td>
                        {r.blockchain ? (
                          <span className="badge badge-verified"><Shield size={9} /> Yes</span>
                        ) : "—"}
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <button
                            className="btn btn-ghost btn-sm"
                            onClick={() => viewReport(r)}
                          >
                            <Eye size={12} /> View
                          </button>
                          <a
                            className="btn btn-ghost btn-sm"
                            href={getDownloadUrl(rId)}
                            download
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            <Download size={12} /> JSON
                          </a>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
