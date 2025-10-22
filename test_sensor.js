const http = require('http');

const data = JSON.stringify({
    count: 20,
    device_id: 'ICE_STORE_24H_002'
});

const options = {
    hostname: 'localhost',
    port: 3000,
    path: '/api/sensor/test-data',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
    }
};

const req = http.request(options, (res) => {
    let body = '';
    res.on('data', (chunk) => {
        body += chunk;
    });
    res.on('end', () => {
        console.log('Response:', body);
    });
});

req.on('error', (e) => {
    console.error('Error:', e);
});

req.write(data);
req.end();
