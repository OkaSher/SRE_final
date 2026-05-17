const express = require('express');
const prometheus = require('prom-client'); // 1. Require prom-client

const app = express();
const PORT = process.env.PORT || 8080;

// 2. Enable default metrics collection (CPU, Memory, Event Loop, GC lag, etc.)
// Enforces a 5-second interval to align perfectly with the Prometheus scrape interval
prometheus.collectDefaultMetrics({
    timeout: 5000,
    register: prometheus.register
});

function fibonacci(n) {
    if (n < 2) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// 3. Expose standard GET /metrics endpoint for Prometheus scraping
app.get('/metrics', async (req, res) => {
    try {
        res.set('Content-Type', prometheus.register.contentType);
        res.end(await prometheus.register.metrics());
    } catch (err) {
        res.status(500).end(err);
    }
});

app.get('/', (req, res) => {
    res.status(200).json({
        status: "UP",
        timestamp: new Date(),
        message: "SRE Capstone target service is running perfectly."
    });
});
  
app.get('/heavy', (req, res) => {
    const cycles = req.query.cycles ? parseInt(req.query.cycles) : 40; 
    
    console.log(`[START] Heavy CPU computation started for Fibonacci(${cycles})`);
    const start = Date.now();
    const result = fibonacci(cycles);
    const duration = Date.now() - start;
    console.log(`[END] Computation finished in ${duration}ms. Result: ${result}`);

    res.status(200).json({
        type: "CPU_INTENSIVE",
        cycles: cycles,
        result: result,
        duration_ms: duration
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Microservice securely listening on port ${PORT}`);
});