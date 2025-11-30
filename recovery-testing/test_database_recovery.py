"""
Database Failure Recovery Testing

Tests database server crash recovery, connection loss handling,
data corruption recovery, and backup/restore procedures.
"""
import pytest
import time
import subprocess
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import logging
from config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    RTO_TARGET_SECONDS, RPO_TARGET_SECONDS, BACKUP_DIR,
    get_timestamp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseRecoveryTester:
    """Test database failure recovery scenarios"""
    
    def __init__(self):
        self.connection = None
        self.backup_file = None
        self.recovery_start_time = None
        self.recovery_end_time = None
        
    def connect_to_database(self, timeout=30):
        """Attempt to connect to database with timeout"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                connection_timeout=timeout
            )
            return True
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect_from_database(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
    
    def is_database_available(self):
        """Check if database is available"""
        try:
            if not self.connection or not self.connection.is_connected():
                return self.connect_to_database(timeout=5)
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Error:
            return False
    
    def create_test_data(self):
        """Create test data for recovery testing"""
        try:
            cursor = self.connection.cursor()
            
            # Insert test user
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name, is_admin, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE email=email
            """, (
                'recovery_test@example.com',
                'hashed_password',
                'Recovery Test User',
                False,
                datetime.now()
            ))
            
            user_id = cursor.lastrowid or 1
            
            # Insert test wallet
            cursor.execute("""
                INSERT INTO wallets (user_id, balance, currency, total_deposited)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE balance=VALUES(balance)
            """, (user_id, 100000.00, 'USD', 100000.00))
            
            self.connection.commit()
            cursor.close()
            logger.info("Test data created successfully")
            return True
        except Error as e:
            logger.error(f"Failed to create test data: {e}")
            self.connection.rollback()
            return False
    
    def create_backup(self):
        """Create database backup"""
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.sql')
            
            # Use mysqldump to create backup
            cmd = [
                'mysqldump',
                f'--host={DB_HOST}',
                f'--port={DB_PORT}',
                f'--user={DB_USER}',
                f'--password={DB_PASSWORD}',
                '--single-transaction',
                '--quick',
                '--lock-tables=false',
                DB_NAME
            ]
            
            with open(self.backup_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup created: {self.backup_file}")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def restore_backup(self, backup_file=None):
        """Restore database from backup"""
        try:
            backup_file = backup_file or self.backup_file
            if not backup_file or not os.path.exists(backup_file):
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Use mysql to restore backup
            cmd = [
                'mysql',
                f'--host={DB_HOST}',
                f'--port={DB_PORT}',
                f'--user={DB_USER}',
                f'--password={DB_PASSWORD}',
                DB_NAME
            ]
            
            with open(backup_file, 'r') as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup restored from: {backup_file}")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return False
    
    def simulate_connection_loss(self):
        """Simulate database connection loss"""
        logger.info("Simulating connection loss...")
        if self.connection and self.connection.is_connected():
            self.connection.close()
        return True
    
    def measure_recovery_time(self, recovery_function):
        """Measure time taken to recover"""
        self.recovery_start_time = time.time()
        result = recovery_function()
        self.recovery_end_time = time.time()
        recovery_time = self.recovery_end_time - self.recovery_start_time
        logger.info(f"Recovery time: {recovery_time:.2f} seconds")
        return result, recovery_time
    
    def verify_data_integrity(self):
        """Verify data integrity after recovery"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Check if test user exists
            cursor.execute("""
                SELECT * FROM users WHERE email = %s
            """, ('recovery_test@example.com',))
            user = cursor.fetchone()
            
            if not user:
                logger.error("Test user not found after recovery")
                return False
            
            # Check if wallet exists
            cursor.execute("""
                SELECT * FROM wallets WHERE user_id = %s
            """, (user['user_id'],))
            wallet = cursor.fetchone()
            
            if not wallet:
                logger.error("Test wallet not found after recovery")
                return False
            
            cursor.close()
            logger.info("Data integrity verified")
            return True
        except Error as e:
            logger.error(f"Data integrity check failed: {e}")
            return False
    
    def test_transaction_rollback(self):
        """Test transaction rollback on failure"""
        try:
            cursor = self.connection.cursor()
            
            # Start transaction
            self.connection.start_transaction()
            
            # Insert test data
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name)
                VALUES (%s, %s, %s)
            """, ('rollback_test@example.com', 'hash', 'Rollback Test'))
            
            # Simulate error and rollback
            self.connection.rollback()
            
            # Verify data was not inserted
            cursor.execute("""
                SELECT * FROM users WHERE email = %s
            """, ('rollback_test@example.com',))
            result = cursor.fetchone()
            
            cursor.close()
            
            if result is None:
                logger.info("Transaction rollback successful")
                return True
            else:
                logger.error("Transaction rollback failed - data was committed")
                return False
        except Error as e:
            logger.error(f"Transaction rollback test failed: {e}")
            return False


# Test Cases

@pytest.fixture
def db_tester():
    """Fixture to create database tester instance"""
    tester = DatabaseRecoveryTester()
    yield tester
    tester.disconnect_from_database()


def test_database_connection_recovery(db_tester):
    """Test database connection recovery after connection loss"""
    logger.info("=" * 80)
    logger.info("TEST: Database Connection Recovery")
    logger.info("=" * 80)
    
    # Step 1: Establish initial connection
    assert db_tester.connect_to_database(), "Initial connection failed"
    logger.info("✓ Initial connection established")
    
    # Step 2: Create test data
    assert db_tester.create_test_data(), "Test data creation failed"
    logger.info("✓ Test data created")
    
    # Step 3: Simulate connection loss
    db_tester.simulate_connection_loss()
    logger.info("✓ Connection loss simulated")
    
    # Step 4: Attempt recovery
    recovery_result, recovery_time = db_tester.measure_recovery_time(
        lambda: db_tester.connect_to_database()
    )
    
    assert recovery_result, "Connection recovery failed"
    logger.info(f"✓ Connection recovered in {recovery_time:.2f} seconds")
    
    # Step 5: Verify data integrity
    assert db_tester.verify_data_integrity(), "Data integrity check failed"
    logger.info("✓ Data integrity verified")
    
    # Step 6: Check RTO compliance
    assert recovery_time < RTO_TARGET_SECONDS, \
        f"Recovery time {recovery_time:.2f}s exceeds RTO target {RTO_TARGET_SECONDS}s"
    logger.info(f"✓ RTO target met ({recovery_time:.2f}s < {RTO_TARGET_SECONDS}s)")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Database Connection Recovery")
    logger.info("=" * 80)


def test_backup_and_restore(db_tester):
    """Test backup and restore procedures"""
    logger.info("=" * 80)
    logger.info("TEST: Backup and Restore Procedures")
    logger.info("=" * 80)
    
    # Step 1: Connect to database
    assert db_tester.connect_to_database(), "Database connection failed"
    logger.info("✓ Connected to database")
    
    # Step 2: Create test data
    assert db_tester.create_test_data(), "Test data creation failed"
    logger.info("✓ Test data created")
    
    # Step 3: Create backup
    backup_start = time.time()
    assert db_tester.create_backup(), "Backup creation failed"
    backup_time = time.time() - backup_start
    logger.info(f"✓ Backup created in {backup_time:.2f} seconds")
    
    # Step 4: Modify data (simulate data loss)
    cursor = db_tester.connection.cursor()
    cursor.execute("DELETE FROM wallets WHERE user_id > 0")
    db_tester.connection.commit()
    cursor.close()
    logger.info("✓ Data modified (simulating data loss)")
    
    # Step 5: Restore from backup
    restore_result, restore_time = db_tester.measure_recovery_time(
        lambda: db_tester.restore_backup()
    )
    
    assert restore_result, "Backup restore failed"
    logger.info(f"✓ Backup restored in {restore_time:.2f} seconds")
    
    # Step 6: Verify data integrity
    assert db_tester.verify_data_integrity(), "Data integrity check failed after restore"
    logger.info("✓ Data integrity verified after restore")
    
    # Step 7: Check RPO compliance
    total_recovery_time = backup_time + restore_time
    assert total_recovery_time < RTO_TARGET_SECONDS, \
        f"Total recovery time {total_recovery_time:.2f}s exceeds RTO target"
    logger.info(f"✓ RTO target met ({total_recovery_time:.2f}s < {RTO_TARGET_SECONDS}s)")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Backup and Restore Procedures")
    logger.info("=" * 80)


def test_transaction_rollback(db_tester):
    """Test transaction rollback on failure"""
    logger.info("=" * 80)
    logger.info("TEST: Transaction Rollback")
    logger.info("=" * 80)
    
    # Step 1: Connect to database
    assert db_tester.connect_to_database(), "Database connection failed"
    logger.info("✓ Connected to database")
    
    # Step 2: Test transaction rollback
    assert db_tester.test_transaction_rollback(), "Transaction rollback test failed"
    logger.info("✓ Transaction rollback verified")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Transaction Rollback")
    logger.info("=" * 80)


def test_connection_pool_recovery(db_tester):
    """Test connection pool recovery after exhaustion"""
    logger.info("=" * 80)
    logger.info("TEST: Connection Pool Recovery")
    logger.info("=" * 80)
    
    connections = []
    
    try:
        # Step 1: Exhaust connection pool
        logger.info("Exhausting connection pool...")
        for i in range(15):  # Try to create more connections than pool size
            try:
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    connection_timeout=5
                )
                connections.append(conn)
                logger.info(f"  Created connection {i+1}")
            except Error as e:
                logger.info(f"  Connection {i+1} failed (expected): {e}")
                break
        
        # Step 2: Close all connections
        logger.info("Closing all connections...")
        for conn in connections:
            if conn.is_connected():
                conn.close()
        connections.clear()
        
        # Step 3: Wait for pool recovery
        time.sleep(2)
        
        # Step 4: Verify new connections can be established
        recovery_result, recovery_time = db_tester.measure_recovery_time(
            lambda: db_tester.connect_to_database()
        )
        
        assert recovery_result, "Connection pool recovery failed"
        logger.info(f"✓ Connection pool recovered in {recovery_time:.2f} seconds")
        
        logger.info("=" * 80)
        logger.info("TEST PASSED: Connection Pool Recovery")
        logger.info("=" * 80)
        
    finally:
        # Cleanup
        for conn in connections:
            if conn.is_connected():
                conn.close()


def test_data_corruption_detection(db_tester):
    """Test data corruption detection and recovery"""
    logger.info("=" * 80)
    logger.info("TEST: Data Corruption Detection")
    logger.info("=" * 80)
    
    # Step 1: Connect to database
    assert db_tester.connect_to_database(), "Database connection failed"
    logger.info("✓ Connected to database")
    
    # Step 2: Create test data
    assert db_tester.create_test_data(), "Test data creation failed"
    logger.info("✓ Test data created")
    
    # Step 3: Create backup before corruption
    assert db_tester.create_backup(), "Backup creation failed"
    logger.info("✓ Backup created")
    
    # Step 4: Simulate data corruption (invalid data)
    try:
        cursor = db_tester.connection.cursor()
        cursor.execute("""
            UPDATE wallets SET balance = -999999.99 WHERE user_id > 0
        """)
        db_tester.connection.commit()
        cursor.close()
        logger.info("✓ Data corruption simulated")
    except Error as e:
        logger.info(f"✓ Data corruption prevented by constraints: {e}")
    
    # Step 5: Detect corruption
    cursor = db_tester.connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM wallets WHERE balance < 0")
    result = cursor.fetchone()
    corrupted_records = result[0] if result else 0
    cursor.close()
    
    if corrupted_records > 0:
        logger.info(f"✓ Detected {corrupted_records} corrupted records")
        
        # Step 6: Restore from backup
        restore_result, restore_time = db_tester.measure_recovery_time(
            lambda: db_tester.restore_backup()
        )
        assert restore_result, "Backup restore failed"
        logger.info(f"✓ Restored from backup in {restore_time:.2f} seconds")
    else:
        logger.info("✓ No corruption detected (prevented by constraints)")
    
    # Step 7: Verify data integrity
    assert db_tester.verify_data_integrity(), "Data integrity check failed"
    logger.info("✓ Data integrity verified")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Data Corruption Detection")
    logger.info("=" * 80)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
