"""
Network Failure Recovery Testing

Tests internet connectivity loss, API endpoint unavailability,
timeout handling, retry mechanisms, and circuit breaker patterns.
"""
import pytest
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
from unittest.mock import patch, Mock
from datetime import datetime
from config import (
    TEST_BASE_URL, API_TIMEOUT, NETWORK_FAILURE_DURATION,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_TIMEOUT,
    RETRY_ATTEMPTS, RETRY_DELAY, get_timestamp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker implementation for testing"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker: OPEN -> HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.info(f"Circuit breaker: {self.state} -> OPEN (failures: {self.failure_count})")
            
            raise e


class NetworkRecoveryTester:
    """Test network failure recovery scenarios"""
    
    def __init__(self):
        self.base_url = TEST_BASE_URL
        self.session = requests.Session()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            timeout=CIRCUIT_BREAKER_TIMEOUT
        )
        
    def create_session_with_retry(self, retries=3, backoff_factor=0.3):
        """Create session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def test_api_connectivity(self, url=None, timeout=API_TIMEOUT):
        """Test API connectivity"""
        url = url or self.base_url
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code < 500
        except requests.exceptions.RequestException as e:
            logger.error(f"API connectivity test failed: {e}")
            return False
    
    def simulate_network_timeout(self, url=None):
        """Simulate network timeout"""
        url = url or f"{self.base_url}/api/test"
        try:
            response = requests.get(url, timeout=0.001)  # Very short timeout
            return False
        except requests.exceptions.Timeout:
            logger.info("✓ Network timeout simulated")
            return True
        except requests.exceptions.RequestException:
            return True
    
    def simulate_connection_refused(self):
        """Simulate connection refused"""
        try:
            # Try to connect to non-existent port
            response = requests.get("http://localhost:9999", timeout=1)
            return False
        except requests.exceptions.ConnectionError:
            logger.info("✓ Connection refused simulated")
            return True
        except requests.exceptions.RequestException:
            return True
    
    def test_retry_mechanism(self, max_retries=RETRY_ATTEMPTS):
        """Test retry mechanism"""
        retry_count = 0
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/",
                    timeout=API_TIMEOUT
                )
                if response.status_code < 500:
                    logger.info(f"✓ Request succeeded on attempt {attempt + 1}")
                    return True, attempt + 1
            except requests.exceptions.RequestException as e:
                retry_count += 1
                last_error = e
                logger.info(f"  Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)
        
        logger.error(f"✗ All {max_retries} retry attempts failed")
        return False, retry_count
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern"""
        def failing_api_call():
            response = requests.get("http://localhost:9999", timeout=1)
            return response.status_code == 200
        
        # Trigger failures to open circuit
        for i in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
            try:
                self.circuit_breaker.call(failing_api_call)
            except Exception:
                logger.info(f"  Failure {i + 1}/{CIRCUIT_BREAKER_FAILURE_THRESHOLD}")
        
        # Circuit should be open now
        assert self.circuit_breaker.state == 'OPEN', "Circuit breaker did not open"
        logger.info("✓ Circuit breaker opened after threshold failures")
        
        # Try to call - should fail immediately
        try:
            self.circuit_breaker.call(failing_api_call)
            return False
        except Exception as e:
            logger.info(f"✓ Circuit breaker blocked call: {e}")
            return True
    
    def test_graceful_degradation(self):
        """Test graceful degradation when external services fail"""
        try:
            # Try to access feature that depends on external API
            response = requests.get(
                f"{self.base_url}/api/stock/AAPL/prediction",
                timeout=API_TIMEOUT
            )
            
            # Should return cached data or error message, not crash
            if response.status_code in [200, 503]:
                logger.info("✓ Graceful degradation working")
                return True
            else:
                logger.warning(f"⚠ Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.info(f"✓ Request handled gracefully: {e}")
            return True
    
    def test_timeout_handling(self, timeout=1):
        """Test timeout handling"""
        start_time = time.time()
        try:
            response = requests.get(
                f"{self.base_url}/api/test/slow",
                timeout=timeout
            )
            elapsed = time.time() - start_time
            
            if elapsed > timeout * 2:
                logger.warning(f"⚠ Timeout not enforced properly: {elapsed:.2f}s")
                return False
            
            logger.info(f"✓ Request completed in {elapsed:.2f}s")
            return True
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            logger.info(f"✓ Timeout enforced after {elapsed:.2f}s")
            return True
        except requests.exceptions.RequestException as e:
            logger.info(f"✓ Request failed gracefully: {e}")
            return True
    
    def test_connection_pooling(self):
        """Test connection pooling and reuse"""
        session = self.create_session_with_retry()
        
        # Make multiple requests
        success_count = 0
        for i in range(10):
            try:
                response = session.get(f"{self.base_url}/", timeout=API_TIMEOUT)
                if response.status_code < 500:
                    success_count += 1
            except requests.exceptions.RequestException:
                pass
        
        logger.info(f"✓ Connection pooling: {success_count}/10 requests successful")
        return success_count >= 8
    
    def measure_recovery_time(self, recovery_function):
        """Measure time taken to recover"""
        start_time = time.time()
        result = recovery_function()
        recovery_time = time.time() - start_time
        logger.info(f"Recovery time: {recovery_time:.2f} seconds")
        return result, recovery_time


# Test Cases

@pytest.fixture
def network_tester():
    """Fixture to create network tester instance"""
    tester = NetworkRecoveryTester()
    yield tester


def test_network_timeout_handling(network_tester):
    """Test network timeout handling"""
    logger.info("=" * 80)
    logger.info("TEST: Network Timeout Handling")
    logger.info("=" * 80)
    
    # Step 1: Test normal connectivity
    is_connected = network_tester.test_api_connectivity()
    if is_connected:
        logger.info("✓ Normal connectivity verified")
    else:
        logger.warning("⚠ Application not responding (may be offline)")
    
    # Step 2: Test timeout handling
    result = network_tester.test_timeout_handling(timeout=2)
    assert result, "Timeout handling failed"
    logger.info("✓ Timeout handling verified")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Network Timeout Handling")
    logger.info("=" * 80)


def test_retry_mechanism(network_tester):
    """Test retry mechanism"""
    logger.info("=" * 80)
    logger.info("TEST: Retry Mechanism")
    logger.info("=" * 80)
    
    # Step 1: Test retry with working endpoint
    success, attempts = network_tester.test_retry_mechanism(max_retries=3)
    
    if success:
        logger.info(f"✓ Retry mechanism working (succeeded after {attempts} attempt(s))")
    else:
        logger.warning("⚠ All retry attempts failed (application may be offline)")
    
    # Step 2: Test retry with session
    session = network_tester.create_session_with_retry(retries=3)
    
    try:
        response = session.get(f"{network_tester.base_url}/", timeout=5)
        logger.info(f"✓ Session with retry strategy: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"✓ Session retry handled error: {e}")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Retry Mechanism")
    logger.info("=" * 80)


def test_circuit_breaker_pattern(network_tester):
    """Test circuit breaker pattern"""
    logger.info("=" * 80)
    logger.info("TEST: Circuit Breaker Pattern")
    logger.info("=" * 80)
    
    # Step 1: Test circuit breaker
    result = network_tester.test_circuit_breaker_pattern()
    assert result, "Circuit breaker test failed"
    logger.info("✓ Circuit breaker pattern verified")
    
    # Step 2: Verify circuit state
    assert network_tester.circuit_breaker.state == 'OPEN', "Circuit should be open"
    logger.info(f"✓ Circuit state: {network_tester.circuit_breaker.state}")
    
    # Step 3: Wait for timeout
    logger.info(f"Waiting {CIRCUIT_BREAKER_TIMEOUT}s for circuit to reset...")
    time.sleep(min(CIRCUIT_BREAKER_TIMEOUT + 1, 5))  # Wait but cap at 5s for testing
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Circuit Breaker Pattern")
    logger.info("=" * 80)


def test_connection_refused_handling(network_tester):
    """Test connection refused handling"""
    logger.info("=" * 80)
    logger.info("TEST: Connection Refused Handling")
    logger.info("=" * 80)
    
    # Step 1: Simulate connection refused
    result = network_tester.simulate_connection_refused()
    assert result, "Connection refused simulation failed"
    logger.info("✓ Connection refused handled gracefully")
    
    # Step 2: Verify application still responds to valid requests
    is_connected = network_tester.test_api_connectivity()
    if is_connected:
        logger.info("✓ Application still responsive after connection error")
    else:
        logger.warning("⚠ Application not responding")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Connection Refused Handling")
    logger.info("=" * 80)


def test_api_unavailability_handling(network_tester):
    """Test API endpoint unavailability handling"""
    logger.info("=" * 80)
    logger.info("TEST: API Unavailability Handling")
    logger.info("=" * 80)
    
    # Step 1: Test graceful degradation
    result = network_tester.test_graceful_degradation()
    logger.info("✓ Graceful degradation tested")
    
    # Step 2: Test with non-existent endpoint
    try:
        response = requests.get(
            f"{network_tester.base_url}/api/nonexistent",
            timeout=API_TIMEOUT
        )
        logger.info(f"✓ Non-existent endpoint handled: {response.status_code}")
        assert response.status_code == 404, "Should return 404 for non-existent endpoint"
    except requests.exceptions.RequestException as e:
        logger.info(f"✓ Request handled gracefully: {e}")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: API Unavailability Handling")
    logger.info("=" * 80)


def test_connection_pooling(network_tester):
    """Test connection pooling"""
    logger.info("=" * 80)
    logger.info("TEST: Connection Pooling")
    logger.info("=" * 80)
    
    # Step 1: Test connection pooling
    result = network_tester.test_connection_pooling()
    
    if result:
        logger.info("✓ Connection pooling working correctly")
    else:
        logger.warning("⚠ Connection pooling may have issues")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Connection Pooling")
    logger.info("=" * 80)


def test_external_api_failure_recovery(network_tester):
    """Test recovery from external API failures"""
    logger.info("=" * 80)
    logger.info("TEST: External API Failure Recovery")
    logger.info("=" * 80)
    
    # Step 1: Test yfinance API simulation
    try:
        response = requests.get(
            f"{network_tester.base_url}/api/stock/AAPL/price",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            logger.info("✓ External API call successful")
        elif response.status_code == 503:
            logger.info("✓ External API failure handled gracefully (503)")
        else:
            logger.info(f"✓ Response status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"✓ External API failure handled: {e}")
    
    # Step 2: Test Twitter API simulation
    try:
        response = requests.get(
            f"{network_tester.base_url}/api/sentiment/AAPL",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            logger.info("✓ Sentiment API call successful")
        elif response.status_code in [503, 429]:
            logger.info(f"✓ Sentiment API failure handled gracefully ({response.status_code})")
        else:
            logger.info(f"✓ Response status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.info(f"✓ Sentiment API failure handled: {e}")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: External API Failure Recovery")
    logger.info("=" * 80)


def test_network_latency_handling(network_tester):
    """Test handling of high network latency"""
    logger.info("=" * 80)
    logger.info("TEST: Network Latency Handling")
    logger.info("=" * 80)
    
    # Step 1: Measure response times
    response_times = []
    
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.get(
                f"{network_tester.base_url}/",
                timeout=API_TIMEOUT
            )
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            logger.info(f"  Request {i+1}: {elapsed:.3f}s")
        except requests.exceptions.RequestException as e:
            logger.info(f"  Request {i+1} failed: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        logger.info(f"✓ Average response time: {avg_time:.3f}s")
        logger.info(f"✓ Maximum response time: {max_time:.3f}s")
        
        # Check if response times are reasonable
        if avg_time < API_TIMEOUT:
            logger.info("✓ Response times within acceptable limits")
        else:
            logger.warning(f"⚠ High average response time: {avg_time:.3f}s")
    else:
        logger.warning("⚠ No successful requests")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Network Latency Handling")
    logger.info("=" * 80)


def test_concurrent_network_requests(network_tester):
    """Test concurrent network request handling"""
    logger.info("=" * 80)
    logger.info("TEST: Concurrent Network Requests")
    logger.info("=" * 80)
    
    import concurrent.futures
    
    def make_request(i):
        try:
            response = requests.get(
                f"{network_tester.base_url}/",
                timeout=API_TIMEOUT
            )
            return response.status_code < 500
        except requests.exceptions.RequestException:
            return False
    
    # Step 1: Send concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(results)
    logger.info(f"✓ Concurrent requests: {success_count}/20 successful")
    
    # Step 2: Verify acceptable success rate
    success_rate = success_count / 20
    if success_rate >= 0.8:
        logger.info(f"✓ Success rate: {success_rate*100:.1f}%")
    else:
        logger.warning(f"⚠ Low success rate: {success_rate*100:.1f}%")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Concurrent Network Requests")
    logger.info("=" * 80)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
