const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();

const corsOptions = {
  origin: 'http://localhost:5173',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
};

// Apply CORS to all routes
app.use(cors(corsOptions));

app.use(express.json());

// Connect to MongoDB
const MONGO_URI =
  process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/plagiarism_auth';

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('MongoDB connected for auth-server');
  })
  .catch((err) => {
    console.error('MongoDB connection error in auth-server:', err);
    process.exit(1);
  });

// Routes
app.use('/api/auth', require('./routes/auth'));

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`Auth server running on port ${PORT}`));