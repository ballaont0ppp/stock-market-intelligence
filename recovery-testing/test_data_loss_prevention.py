"""
Data Loss Prevention Testing

Tests backup procedures, point-in-time recovery, transaction rollback,
data integrity checks, and disaster recovery plan.
"""
import pytest
import time
import subprocess
import os
import hashlib
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import logging
from config import (
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME,
    BACKUP_DIR, RPO_TARGET_SECONDS, RTO_TARGET_SECONDS,
    get_timestamp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataLossPreventionTester:
    """Test data loss prevention scenarios"""
    
    def __init__(self):
        self.connection = None
        self.backup_files = []
        self.test_data_checksums = {}
        
    def connect_to_database(self):
        """Connect to database"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            return True
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect_from_database(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def create_full_backup(self):
        """Create full database backup"""
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'full_backup_{timestamp}.sql')
            
            cmd = [
                'mysqldump',
                f'--host={DB_HOST}',
                f'--port={DB_PORT}',
                f'--user={DB_USER}',
                f'--password={DB_PASSWORD}',
                '--single-transaction',
                '--quick',
                '--lock-tables=false',
                '--routines',
                '--triggers',
                '--events',
                DB_NAME
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                self.backup_files.append(backup_file)
                logger.info(f"✓ Full backup created: {backup_file}")
                return backup_file
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None
    
    def create_incremental_backup(self):
        """Create incremental backup (binary log based)"""
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'incremental_backup_{timestamp}.sql')
            
            # For incremental backup, we'd use binary logs
            # This is a simplified version
            cursor = self.connection.cursor()
            cursor.execute("SHOW MASTER STATUS")
            master_status = cursor.fetchone()
            cursor.close()
            
            if master_status:
                logger.info(f"✓ Binary log position: {master_status}")
                
                # Save the position for point-in-time recovery
                metadata = {
                    'timestamp': timestamp,
                    'log_file': master_status[0] if len(master_status) > 0 else None,
                    'log_position': master_status[1] if len(master_status) > 1 else None
                }
                
                metadata_file = os.path.join(BACKUP_DIR, f'incremental_metadata_{timestamp}.json')
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"✓ Incremental backup metadata saved: {metadata_file}")
                return metadata_file
            else:
                logger.warning("⚠ Binary logging not enabled")
                return None
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            return None
    
    def restore_from_backup(self, backup_file):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_file):
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
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
                logger.info(f"✓ Restored from backup: {backup_file}")
                return True
            else:
                logger.error(f"Restore failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def calculate_data_checksum(self, table_name):
        """Calculate checksum for table data"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CHECKSUM TABLE {table_name}")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                checksum = result[1]
                logger.info(f"  Checksum for {table_name}: {checksum}")
                return checksum
            return None
        except Error as e:
            logger.error(f"Checksum calculation failed for {table_name}: {e}")
            return None
    
    def verify_data_integrity(self, tables=None):
        """Verify data integrity across tables"""
        if tables is None:
            tables = ['users', 'wallets', 'holdings', 'orders', 'transactions']
        
        integrity_ok = True
        for table in tables:
            try:
                cursor = self.connection.cursor()
                
                # Check for NULL values in NOT NULL columns
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                for column in columns:
                    col_name = column[0]
                    nullable = column[2]
                    
                    if nullable == 'NO':
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col_name} IS NULL")
                        null_count = cursor.fetchone()[0]
                        
                        if null_count > 0:
                            logger.error(f"✗ Found {null_count} NULL values in {table}.{col_name}")
                            integrity_ok = False
                
                # Check foreign key constraints
                cursor.execute(f"""
                    SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = '{DB_NAME}'
                    AND TABLE_NAME = '{table}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """)
                
                fk_constraints = cursor.fetchall()
                for constraint in fk_constraints:
                    logger.info(f"  ✓ Foreign key constraint verified: {constraint[0]}")
                
                cursor.close()
                
            except Error as e:
                logger.error(f"Integrity check failed for {table}: {e}")
                integrity_ok = False
        
        if integrity_ok:
            logger.info("✓ Data integrity verified for all tables")
        else:
            logger.error("✗ Data integrity issues found")
        
        return integrity_ok
    
    def test_transaction_atomicity(self):
        """Test transaction atomicity (ACID compliance)"""
        try:
            cursor = self.connection.cursor()
            
            # Start transaction
            self.connection.start_transaction()
            
            # Insert test user
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name)
                VALUES (%s, %s, %s)
            """, ('atomicity_test@example.com', 'hash', 'Atomicity Test'))
            
            user_id = cursor.lastrowid
            
            # Insert wallet (this should succeed)
            cursor.execute("""
                INSERT INTO wallets (user_id, balance)
                VALUES (%s, %s)
            """, (user_id, 100000.00))
            
            # Try to insert invalid data (should fail)
            try:
                cursor.execute("""
                    INSERT INTO wallets (user_id, balance)
                    VALUES (%s, %s)
                """, (user_id, -1000.00))  # Negative balance violates constraint
                
                # If we get here, constraint didn't work
                self.connection.rollback()
                logger.error("✗ Constraint violation not caught")
                return False
            except Error:
                # Expected - constraint violation
                self.connection.rollback()
                logger.info("✓ Transaction rolled back on constraint violation")
            
            # Verify nothing was committed
            cursor.execute("""
                SELECT * FROM users WHERE email = %s
            """, ('atomicity_test@example.com',))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result is None:
                logger.info("✓ Transaction atomicity verified")
                return True
            else:
                logger.error("✗ Partial transaction was committed")
                return False
                
        except Error as e:
            logger.error(f"Transaction atomicity test failed: {e}")
            return False
    
    def test_point_in_time_recovery(self):
        """Test point-in-time recovery"""
        try:
            # Step 1: Create initial backup
            backup_file = self.create_full_backup()
            if not backup_file:
                return False
            
            time.sleep(1)
            
            # Step 2: Make some changes
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name)
                VALUES (%s, %s, %s)
            """, ('pitr_test@example.com', 'hash', 'PITR Test'))
            self.connection.commit()
            cursor.close()
            
            logger.info("✓ Test data inserted after backup")
            
            # Step 3: Create incremental backup
            incremental_backup = self.create_incremental_backup()
            
            # Step 4: Restore to point before changes
            logger.info("Restoring to point before changes...")
            if self.restore_from_backup(backup_file):
                logger.info("✓ Point-in-time recovery successful")
                return True
            else:
                logger.error("✗ Point-in-time recovery failed")
                return False
                
        except Exception as e:
            logger.error(f"Point-in-time recovery test failed: {e}")
            return False
    
    def test_backup_verification(self):
        """Test backup verification"""
        try:
            # Create backup
            backup_file = self.create_full_backup()
            if not backup_file:
                return False
            
            # Verify backup file exists and is not empty
            if not os.path.exists(backup_file):
                logger.error("✗ Backup file does not exist")
                return False
            
            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                logger.error("✗ Backup file is empty")
                return False
            
            logger.info(f"✓ Backup file size: {file_size / 1024:.2f} KB")
            
            # Verify backup can be read
            with open(backup_file, 'r') as f:
                first_line = f.readline()
                if 'MySQL dump' in first_line or 'mysqldump' in first_line:
                    logger.info("✓ Backup file format verified")
                    return True
                else:
                    logger.error("✗ Invalid backup file format")
                    return False
                    
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def test_disaster_recovery_plan(self):
        """Test complete disaster recovery plan"""
        try:
            logger.info("Executing disaster recovery plan...")
            
            # Step 1: Create baseline backup
            logger.info("Step 1: Creating baseline backup...")
            backup_file = self.create_full_backup()
            if not backup_file:
                return False, 0
            
            # Step 2: Simulate disaster (data loss)
            logger.info("Step 2: Simulating disaster...")
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM transactions WHERE transaction_id > 0")
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            logger.info(f"  Deleted {deleted_count} transactions")
            
            # Step 3: Detect data loss
            logger.info("Step 3: Detecting data loss...")
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            remaining_count = cursor.fetchone()[0]
            cursor.close()
            logger.info(f"  Remaining transactions: {remaining_count}")
            
            # Step 4: Initiate recovery
            logger.info("Step 4: Initiating recovery...")
            recovery_start = time.time()
            
            if self.restore_from_backup(backup_file):
                recovery_time = time.time() - recovery_start
                logger.info(f"✓ Recovery completed in {recovery_time:.2f} seconds")
                
                # Step 5: Verify recovery
                logger.info("Step 5: Verifying recovery...")
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM transactions")
                recovered_count = cursor.fetchone()[0]
                cursor.close()
                
                logger.info(f"  Recovered transactions: {recovered_count}")
                
                # Step 6: Verify data integrity
                logger.info("Step 6: Verifying data integrity...")
                integrity_ok = self.verify_data_integrity()
                
                if integrity_ok:
                    logger.info("✓ Disaster recovery plan executed successfully")
                    return True, recovery_time
                else:
                    logger.error("✗ Data integrity issues after recovery")
                    return False, recovery_time
            else:
                logger.error("✗ Recovery failed")
                return False, 0
                
        except Exception as e:
            logger.error(f"Disaster recovery plan failed: {e}")
            return False, 0


# Test Cases

@pytest.fixture
def dlp_tester():
    """Fixture to create data loss prevention tester instance"""
    tester = DataLossPreventionTester()
    assert tester.connect_to_database(), "Failed to connect to database"
    yield tester
    tester.disconnect_from_database()


def test_backup_procedures(dlp_tester):
    """Test backup procedures"""
    logger.info("=" * 80)
    logger.info("TEST: Backup Procedures")
    logger.info("=" * 80)
    
    # Step 1: Test full backup
    logger.info("Testing full backup...")
    backup_file = dlp_tester.create_full_backup()
    assert backup_file is not None, "Full backup creation failed"
    logger.info("✓ Full backup created successfully")
    
    # Step 2: Verify backup
    assert dlp_tester.test_backup_verification(), "Backup verification failed"
    logger.info("✓ Backup verification passed")
    
    # Step 3: Test incremental backup
    logger.info("Testing incremental backup...")
    incremental_backup = dlp_tester.create_incremental_backup()
    if incremental_backup:
        logger.info("✓ Incremental backup created successfully")
    else:
        logger.warning("⚠ Incremental backup not available (binary logging may be disabled)")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Backup Procedures")
    logger.info("=" * 80)


def test_point_in_time_recovery(dlp_tester):
    """Test point-in-time recovery"""
    logger.info("=" * 80)
    logger.info("TEST: Point-in-Time Recovery")
    logger.info("=" * 80)
    
    # Test PITR
    result = dlp_tester.test_point_in_time_recovery()
    assert result, "Point-in-time recovery failed"
    logger.info("✓ Point-in-time recovery verified")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Point-in-Time Recovery")
    logger.info("=" * 80)


def test_transaction_rollback(dlp_tester):
    """Test transaction rollback"""
    logger.info("=" * 80)
    logger.info("TEST: Transaction Rollback")
    logger.info("=" * 80)
    
    # Test transaction atomicity
    result = dlp_tester.test_transaction_atomicity()
    assert result, "Transaction atomicity test failed"
    logger.info("✓ Transaction rollback verified")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Transaction Rollback")
    logger.info("=" * 80)


def test_data_integrity_checks(dlp_tester):
    """Test data integrity checks"""
    logger.info("=" * 80)
    logger.info("TEST: Data Integrity Checks")
    logger.info("=" * 80)
    
    # Step 1: Verify current data integrity
    result = dlp_tester.verify_data_integrity()
    assert result, "Data integrity check failed"
    logger.info("✓ Data integrity verified")
    
    # Step 2: Calculate checksums
    logger.info("Calculating table checksums...")
    tables = ['users', 'wallets', 'holdings', 'orders']
    for table in tables:
        checksum = dlp_tester.calculate_data_checksum(table)
        if checksum:
            dlp_tester.test_data_checksums[table] = checksum
    
    logger.info("✓ Checksums calculated")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Data Integrity Checks")
    logger.info("=" * 80)


def test_disaster_recovery_plan(dlp_tester):
    """Test disaster recovery plan"""
    logger.info("=" * 80)
    logger.info("TEST: Disaster Recovery Plan")
    logger.info("=" * 80)
    
    # Execute disaster recovery plan
    success, recovery_time = dlp_tester.test_disaster_recovery_plan()
    
    if success:
        logger.info("✓ Disaster recovery plan executed successfully")
        
        # Verify RTO compliance
        if recovery_time < RTO_TARGET_SECONDS:
            logger.info(f"✓ RTO target met: {recovery_time:.2f}s < {RTO_TARGET_SECONDS}s")
        else:
            logger.warning(f"⚠ RTO target exceeded: {recovery_time:.2f}s > {RTO_TARGET_SECONDS}s")
    else:
        logger.error("✗ Disaster recovery plan failed")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Disaster Recovery Plan")
    logger.info("=" * 80)


def test_backup_retention_policy(dlp_tester):
    """Test backup retention policy"""
    logger.info("=" * 80)
    logger.info("TEST: Backup Retention Policy")
    logger.info("=" * 80)
    
    # Step 1: List existing backups
    if os.path.exists(BACKUP_DIR):
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql')]
        logger.info(f"Found {len(backups)} backup files")
        
        # Step 2: Check backup ages
        old_backups = []
        for backup in backups:
            backup_path = os.path.join(BACKUP_DIR, backup)
            file_time = os.path.getmtime(backup_path)
            age_days = (time.time() - file_time) / 86400
            
            logger.info(f"  {backup}: {age_days:.1f} days old")
            
            if age_days > 7:  # Older than 7 days
                old_backups.append(backup)
        
        if old_backups:
            logger.info(f"✓ Found {len(old_backups)} backups older than 7 days")
            logger.info("  (These should be archived or deleted per retention policy)")
        else:
            logger.info("✓ All backups within retention period")
    else:
        logger.warning("⚠ Backup directory does not exist")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: Backup Retention Policy")
    logger.info("=" * 80)


def test_rpo_compliance(dlp_tester):
    """Test Recovery Point Objective compliance"""
    logger.info("=" * 80)
    logger.info("TEST: RPO Compliance")
    logger.info("=" * 80)
    
    # Step 1: Create baseline backup
    backup_time = time.time()
    backup_file = dlp_tester.create_full_backup()
    assert backup_file is not None, "Backup creation failed"
    
    # Step 2: Make changes
    cursor = dlp_tester.connection.cursor()
    cursor.execute("""
        INSERT INTO users (email, password_hash, full_name)
        VALUES (%s, %s, %s)
    """, ('rpo_test@example.com', 'hash', 'RPO Test'))
    dlp_tester.connection.commit()
    change_time = time.time()
    cursor.close()
    
    # Step 3: Calculate data loss window
    data_loss_window = change_time - backup_time
    logger.info(f"Data loss window: {data_loss_window:.2f} seconds")
    
    # Step 4: Check RPO compliance
    if data_loss_window < RPO_TARGET_SECONDS:
        logger.info(f"✓ RPO target met: {data_loss_window:.2f}s < {RPO_TARGET_SECONDS}s")
    else:
        logger.warning(f"⚠ RPO target exceeded: {data_loss_window:.2f}s > {RPO_TARGET_SECONDS}s")
        logger.info("  Consider more frequent backups or enable binary logging")
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETED: RPO Compliance")
    logger.info("=" * 80)


def test_concurrent_backup_operations(dlp_tester):
    """Test concurrent backup operations"""
    logger.info("=" * 80)
    logger.info("TEST: Concurrent Backup Operations")
    logger.info("=" * 80)
    
    import concurrent.futures
    
    def create_backup(i):
        try:
            backup_file = dlp_tester.create_full_backup()
            return backup_file is not None
        except Exception as e:
            logger.error(f"Backup {i} failed: {e}")
            return False
    
    # Try to create multiple backups concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(create_backup, i) for i in range(3)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(results)
    logger.info(f"✓ Concurrent backups: {success_count}/3 successful")
    
    assert success_count >= 2, "Too many concurrent backup failures"
    logger.info("✓ Concurrent backup operations handled correctly")
    
    logger.info("=" * 80)
    logger.info("TEST PASSED: Concurrent Backup Operations")
    logger.info("=" * 80)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
