import logging
from locust import HttpUser, task, between

# ==============================================================================
# SRE OBSERVABILITY CONFIGURATION
# ==============================================================================
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [SRE-LOAD-TEST] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("sre_stress_test")

class MicroserviceStressTester(HttpUser):
    """
    Locust User class to simulate SRE stress testing scenarios.
    Specially biased towards heavy CPU computation to validate GCP auto-scaling
    policies by driving target instance CPU utilization above 70%.
    """
    
    # Default Target URL - exposes the GCP production VM
    host = "http://35.202.129.148:8080"
    
    # Simulate realistic user think time (1 to 3 seconds) between requests.
    # This models a realistic concurrent traffic profile rather than a simple DOS.
    wait_time = between(1, 3)

    @task(1)
    def test_root_endpoint(self):
        """
        [Light Task] Simulates standard home page / health check traffic.
        Weight: 1 (20% of traffic share).
        This endpoints consumes minimal CPU/RAM and responds quickly under normal load.
        """
        logger.debug("Dispatching GET request to Root (/) endpoint.")
        
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                err_msg = f"Root endpoint failed with unexpected status code: {response.status_code}"
                response.failure(err_msg)
                logger.error(err_msg)

    @task(4)
    def test_heavy_cpu_endpoint(self):
        """
        [Heavy Task] Simulates high CPU-intensive transactions.
        Weight: 4 (80% of traffic share).
        This executes recursive Fibonacci calculations (43 cycles) on the Node.js target,
        deliberately saturating the single-threaded V8 event loop. This quickly drives
        host CPU consumption above 70% to trigger GCP Managed Instance Group scaling.
        """
        logger.debug("Dispatching GET request to Heavy (/heavy) endpoint.")
        
        # 15s timeout: if the Node event loop is blocked, requests will timeout and be caught as failures
        with self.client.get("/heavy?cycles=35", timeout=15.0, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    payload = response.json()
                    # Validate SRE metric integrity in response payload
                    if "result" in payload and "duration_ms" in payload:
                        response.success()
                        logger.info(f"Heavy computation successful. Result: {payload['result']} (Took: {payload['duration_ms']}ms)")
                    else:
                        err_msg = "Payload validation failed: missing 'result' or 'duration_ms'"
                        response.failure(err_msg)
                        logger.error(err_msg)
                except ValueError:
                    err_msg = "Payload parsing failed: Response is not valid JSON"
                    response.failure(err_msg)
                    logger.error(err_msg)
            elif response.status_code == 0:
                # Occurs if there is a connection reset, DNS failure, or connection timeout due to CPU lockup
                err_msg = "Connection timeout or reset. The event loop may be fully saturated!"
                response.failure(err_msg)
                logger.critical(err_msg)
            else:
                err_msg = f"Heavy endpoint failed with status code: {response.status_code}"
                response.failure(err_msg)
                logger.error(err_msg)
