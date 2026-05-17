const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

function fibonacci(n) {
    if (n < 2) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

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