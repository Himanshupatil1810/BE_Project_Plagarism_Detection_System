import api from './axios.js'

// POST /check  — multipart/form-data
export const checkPlagiarism = async (file, userId) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('user_id', userId)
  formData.append('store_on_blockchain', 'true')

  const { data } = await api.post('/check', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

// GET /verify/:hash
export const verifyReport = async (reportHash) => {
  const { data } = await api.get(`/verify/${reportHash}`)
  return data
}

// GET /reports/:userId
export const getUserReports = async (userId) => {
  const { data } = await api.get(`/reports/${userId}`)
  return data
}

// GET /download/:id  — returns URL
export const getDownloadUrl = (reportId) =>
  `http://localhost:5000/download/${reportId}`
