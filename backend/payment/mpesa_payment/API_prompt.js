const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

app.get('/mpesa/token', async (req, res) => {
  const { CONSUMER_KEY, CONSUMER_SECRET } = process.env;
  const auth = Buffer.from(`${CONSUMER_KEY}:${CONSUMER_SECRET}`).toString('base64');
  try {
    const { data } = await axios.get(
      'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
      { headers: { Authorization: `Basic ${auth}` } }
    );
    res.json({ token: data.access_token });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
