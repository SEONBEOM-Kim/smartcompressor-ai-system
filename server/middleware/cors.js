const cors = require('cors');

const corsMiddleware = cors({
    origin: ['http://localhost:3000', 'http://3.39.124.0:3000', 'https://signalcraft.kr'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
});

module.exports = corsMiddleware;