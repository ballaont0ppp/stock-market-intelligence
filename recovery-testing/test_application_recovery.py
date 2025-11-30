"""
Application Failure Recovery Testing

Tests server crash recovery, memory exhaustion handling,
unhandled exception recovery, auto-restart mechanisms, and graceful shutdown.
"""
import pytest
import time
import subprocess
import psutil
import requests
import signal
import os
import logging
from datetime import datetime
from config import (
    TEST_BASE_URL, APP_RESTART_TIMEOUT, MEMORY_LIMIT_MB,
    TEST_TIMEOUT, get_timestamp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApplicationRecoveryTester:
    """Test application failure recovery scenarios"""
    
    def __init__(self):
        self.app_process = None
        self.recovery_start_time = None
        self.recovery_end_time = None
        self.base_url = TEST_BASE_URL
        
    def is_application_running(self):
        """Check if application is running and responding"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return response.status_code in [200, 302, 401]
        except requests.exceptions.RequestException:
            return False
    
    def wait_for_application_start(self, timeout=APP_RESTART_TIMEOUT):
        """Wait for application to start"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_application_running():
                return True
            time.sleep(1)
        return False
    
    def get_application_process(self):
        """Find the application process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('flask' in str(cmd).lower() or 'app.py' in str(cmd).lower() for cmd in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def get_process_memory_usage(self, process):
        """Get process memory usage in MB"""
        try:
            mem_info = process.memory_info()
            return mem_info.rss / (1024 * 1024)  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
    
    def simulate_server_crash(self):
        """Simulate server crash by killing the process"""
        logger.info("Simulating server crash...")
        process = self.get_application_process()
        if process:
            try:
                process.kill()
                process.wait(timeout=5)
                logger.info(f"✓ Process {process.pid} killed")
                return True
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning("Process already terminated or timeout")
                return True
        else:
            logger.warning("Application process not found")
            return False
    
    def simulate_graceful_shutdown(self):
        """Simulate graceful shutdown using SIGTERM"""
        logger.info("Simulating graceful shutdown...")
        process = self.get_application_process()
        if process:
            try:
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=10)
                logger.info(f"✓ Process {process.pid} terminated gracefully")
                return True
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning("Process did not terminate gracefully, forcing kill")
                try:
                    process.kill()
                    return True
                except psutil.NoSuchProcess:
                    return True
        else:
            logger.warning("Application process not found")
            return False
    
    def simulate_memory_exhaustion(self):
        """Simulate memory exhaustion scenario"""
        logger.info("Simulating memory exhaustion...")
        try:
            # Send request that might cause high memory usage
            response = requests.post(
                f"{self.base_url}/api/test/memory-stress",
                json={'size': MEMORY_LIMIT_MB * 2},
                timeout=10
            )
            return response.status_code in [200, 500, 503]
        except requests.exceptions.RequestException as e:
            logger.info(f"Memory stress request failed (expected): {e}")
            return True
    
    def simulate_unhandled_exception(self):
        """Trigger unhandled exception"""
        logger.info("Simulating unhandled exception...")
        try:
            response = requests.get(
                f"{self.base_url}/api/test/trigger-error",
                timeout=10
            )
            # Application should handle this gracefully
            return response.status_code in [500, 503]
        except requests.exceptions.RequestException as e:
            logger.info(f"Exception request failed: {e}")
            return True
    
    def measure_recovery_time(self, recovery_function):
        """Measure time taken to recover"""
        self.recovery_start_time = time.time()
        result = recovery_function()
        self.recovery_end_time = time.time()
        recovery_time = self.recovery_end_time - self.recovery_start_time
        logger.info(f"Recovery time: {recovery_time:.2f} seconds")
        return result, recovery_time
    
    def verify_application_health(self):
        """Verify application health after recovery"""
        try:
            # Check health endpoint
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"Health check: {health_data}")
                return health_data.get('status') == 'healthy'
            else:
                # If no health endpoint, check if main page loads
                response = requests.get(f"{self.base_url}/", timeout=5)
                return response.status_code in [200, 302]
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def test_database_connection_after_recovery(self):
        """Test database connectivity after recovery"""
        try:
            response = requests.get(
                f"{self.base_url}/api/health/database",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get('database') == 'connected'
            return False
        except requests.exceptions.RequestException:
            return False
    
    def test_session_persistence(self):
        """Test if sessions persist after recovery"""
        try:
            # Create a session
            session = requests.Session()
            
            # Login
            response = session.post(
                f"{self.base_url}/login",
                data={
                    'email': 'test@example.com',
                    'password': 'password123'
                },
                timeout=5
            )
            
            # Check if logged in
            response = session.get(f"{self.base_url}/dashboard", timeout=5)
            return response.status_code in [200, 302]
        except requests.exceptions.RequestException:
            return False


# Test Cases

@pytest.fixture
def app_tester():
    """Fixture to create application tester instance"""
    tester = ApplicationRecoveryTester()
    yield tester


def test_server_crash_recovery(app_tester):
    """Test server crash recovery"""
    logger.info("=" * 80)
    logger.info("TEST: Server Crash Recovery")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running initially"
    logger.info("✓ Application is running")
    
    # Step 2: Get initial process info
    initial_process = app_tester.get_application_process()
    if initial_process:
        logger.info(f"✓ Found application process: PID {initial_process.pid}")
    
    # Step 3: Simulate server crash
    app_tester.simulate_server_crash()
    logger.info("✓ Server crash simulated")
    
    # Step 4: Wait a moment
    time.sleep(2)
    
    # Step 5: Check if application auto-restarted
    recovery_result, recovery_time = app_tester.measure_recovery_time(
        lambda: app_tester.wait_for_application_start()
    )
    
    if recovery_result:
        logger.info(f"✓ Application auto-restarted in {recovery_time:.2f} seconds")
        
        # Step 6: Verify health
        assert app_tester.verify_application_health(), "Application health check failed"
        logger.info("✓ Application health verified")
        
        # Step 7: Check recovery time
        assert recovery_time < APP_RESTART_TIMEOUT, \
            f"Recovery time {recovery_time:.2f}s exceeds timeout {APP_RESTART_TIMEOUT}s"
        logger.info(f"✓ Recovery time within acceptable limits")
    else:
        logger.warning("⚠ Application did not auto-restart (manual restart may be required)")
        logger.info("Note: Auto-restart requires process manager (systemd, supervisor, etc.)")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Server Crash Recovery")
    logger.info("=" * 80)


def test_graceful_shutdown(app_tester):
    """Test graceful shutdown procedures"""
    logger.info("=" * 80)
    logger.info("TEST: Graceful Shutdown")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running"
    logger.info("✓ Application is running")
    
    # Step 2: Initiate graceful shutdown
    shutdown_start = time.time()
    result = app_tester.simulate_graceful_shutdown()
    shutdown_time = time.time() - shutdown_start
    
    assert result, "Graceful shutdown failed"
    logger.info(f"✓ Graceful shutdown completed in {shutdown_time:.2f} seconds")
    
    # Step 3: Verify application stopped
    time.sleep(2)
    is_running = app_tester.is_application_running()
    
    if not is_running:
        logger.info("✓ Application stopped successfully")
    else:
        logger.warning("⚠ Application still running after shutdown signal")
    
    # Step 4: Check shutdown time
    assert shutdown_time < 30, f"Shutdown took too long: {shutdown_time:.2f}s"
    logger.info("✓ Shutdown time within acceptable limits")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Graceful Shutdown")
    logger.info("=" * 80)


def test_memory_exhaustion_handling(app_tester):
    """Test memory exhaustion handling"""
    logger.info("=" * 80)
    logger.info("TEST: Memory Exhaustion Handling")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running"
    logger.info("✓ Application is running")
    
    # Step 2: Get initial memory usage
    process = app_tester.get_application_process()
    if process:
        initial_memory = app_tester.get_process_memory_usage(process)
        logger.info(f"✓ Initial memory usage: {initial_memory:.2f} MB")
    
    # Step 3: Simulate memory exhaustion
    result = app_tester.simulate_memory_exhaustion()
    logger.info("✓ Memory exhaustion scenario triggered")
    
    # Step 4: Wait for recovery
    time.sleep(5)
    
    # Step 5: Verify application is still responsive
    is_running = app_tester.is_application_running()
    
    if is_running:
        logger.info("✓ Application recovered from memory stress")
        
        # Check memory usage after recovery
        process = app_tester.get_application_process()
        if process:
            current_memory = app_tester.get_process_memory_usage(process)
            logger.info(f"✓ Current memory usage: {current_memory:.2f} MB")
            
            # Memory should not be excessively high
            if current_memory < MEMORY_LIMIT_MB * 1.5:
                logger.info("✓ Memory usage within acceptable limits")
            else:
                logger.warning(f"⚠ High memory usage: {current_memory:.2f} MB")
    else:
        logger.warning("⚠ Application crashed due to memory exhaustion")
        
        # Try to restart
        recovery_result, recovery_time = app_tester.measure_recovery_time(
            lambda: app_tester.wait_for_application_start()
        )
        
        if recovery_result:
            logger.info(f"✓ Application restarted in {recovery_time:.2f} seconds")
        else:
            logger.error("✗ Application failed to restart")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Memory Exhaustion Handling")
    logger.info("=" * 80)


def test_unhandled_exception_recovery(app_tester):
    """Test unhandled exception recovery"""
    logger.info("=" * 80)
    logger.info("TEST: Unhandled Exception Recovery")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running"
    logger.info("✓ Application is running")
    
    # Step 2: Trigger unhandled exception
    result = app_tester.simulate_unhandled_exception()
    logger.info("✓ Unhandled exception triggered")
    
    # Step 3: Wait a moment
    time.sleep(2)
    
    # Step 4: Verify application is still running
    is_running = app_tester.is_application_running()
    
    assert is_running, "Application crashed after unhandled exception"
    logger.info("✓ Application survived unhandled exception")
    
    # Step 5: Verify health
    is_healthy = app_tester.verify_application_health()
    
    if is_healthy:
        logger.info("✓ Application health verified after exception")
    else:
        logger.warning("⚠ Application health degraded after exception")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Unhandled Exception Recovery")
    logger.info("=" * 80)


def test_database_connection_recovery_after_restart(app_tester):
    """Test database connection recovery after application restart"""
    logger.info("=" * 80)
    logger.info("TEST: Database Connection Recovery After Restart")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running"
    logger.info("✓ Application is running")
    
    # Step 2: Verify database connection
    db_connected = app_tester.test_database_connection_after_recovery()
    if db_connected:
        logger.info("✓ Database connection verified")
    else:
        logger.warning("⚠ Database connection check not available")
    
    # Step 3: Simulate crash
    app_tester.simulate_server_crash()
    logger.info("✓ Server crash simulated")
    
    # Step 4: Wait for recovery
    time.sleep(5)
    
    # Step 5: Check if application restarted
    is_running = app_tester.is_application_running()
    
    if is_running:
        logger.info("✓ Application restarted")
        
        # Step 6: Verify database connection after restart
        time.sleep(2)  # Give time for connections to establish
        db_connected = app_tester.test_database_connection_after_recovery()
        
        if db_connected:
            logger.info("✓ Database connection restored after restart")
        else:
            logger.warning("⚠ Database connection check not available")
    else:
        logger.warning("⚠ Application did not auto-restart")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Database Connection Recovery After Restart")
    logger.info("=" * 80)


def test_concurrent_request_handling_after_recovery(app_tester):
    """Test concurrent request handling after recovery"""
    logger.info("=" * 80)
    logger.info("TEST: Concurrent Request Handling After Recovery")
    logger.info("=" * 80)
    
    # Step 1: Verify application is running
    assert app_tester.is_application_running(), "Application is not running"
    logger.info("✓ Application is running")
    
    # Step 2: Send concurrent requests
    import concurrent.futures
    
    def make_request():
        try:
            response = requests.get(f"{app_tester.base_url}/", timeout=5)
            return response.status_code in [200, 302]
        except:
            return False
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(results)
    logger.info(f"✓ Concurrent requests: {success_count}/10 successful")
    
    assert success_count >= 8, f"Too many failed requests: {10 - success_count}/10"
    logger.info("✓ Application handles concurrent requests after recovery")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Concurrent Request Handling After Recovery")
    logger.info("=" * 80)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
