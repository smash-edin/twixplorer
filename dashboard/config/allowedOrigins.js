const allowedOrigins = [
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5000',
    'http://localhost:3000',
    'http://localhost:5000',
    // If the server from which the Flask API is running is different from that of the React front-end, add the IP
    // address of the former with port 3000 and 5000 respectively
];
module.exports = allowedOrigins;