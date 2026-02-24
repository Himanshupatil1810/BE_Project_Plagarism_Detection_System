// CHANGE: Import analysisApi specifically from your updated axios.js
import { analysisApi } from './axios.js';

// POST /check — multipart/form-data
// Corrected flow in plagiarismApi.js
export const checkPlagiarism = async (file, userId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId); // Sending the MongoDB ID to Flask
  formData.append('store_on_blockchain', 'true');

  const { data } = await analysisApi.post('/check', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

// GET /verify/:hash
export const verifyReport = async (reportHash) => {
  // CHANGE: Use analysisApi instead of generic api
  console.log("API is hitting.")
  const { data } = await analysisApi.get(`/verify/${reportHash}`);
  console.log(data);
  return data;
};

// GET /reports/:userId
export const getUserReports = async (userId) => {
  // CHANGE: Use analysisApi instead of generic api
  console.log("Getting history of uploads...");
  const { data } = await analysisApi.get(`/reports/${userId}`);
  console.log(data);
  return data;
};

// GET /download/:id — returns URL
export const getDownloadUrl = (reportId) =>
  `http://localhost:5000/download/${reportId}`;