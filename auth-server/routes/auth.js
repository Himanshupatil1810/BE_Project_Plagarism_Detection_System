const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Signup Route
router.post('/signup', async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Check if user exists
    let user = await User.findOne({ email });
    if (user) return res.status(400).json({ message: 'User already exists' });

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create unique user_id for Flask integration
    const user_id = `user_${Date.now()}`;

    user = new User({
      name,
      email,
      password: hashedPassword,
      user_id
    });

    await user.save();

    const token = jwt.sign(
      { user_id: user.user_id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    res.json({ token, user: { name, email, user_id } });
  } catch (err) {
    console.error('Signup error:', err);
    res
      .status(500)
      .json({ message: 'Server error during signup. Please try again.' });
  }
});

// Login Route
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid Credentials' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid Credentials' });
    }

    const token = jwt.sign(
      { user_id: user.user_id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    res.json({
      token,
      user: {
        name: user.name,
        email: user.email,
        user_id: user.user_id,
      },
    });
  } catch (err) {
    console.error('Login error:', err);
    res
      .status(500)
      .json({ message: 'Server error during login. Please try again.' });
  }
});

module.exports = router;