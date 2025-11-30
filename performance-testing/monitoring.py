"""
Performance Monitoring Module

Collects system metrics during performance tests
"""

import psutil
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict
import json


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float


class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self, interval: int = 5):
        """
        Initialize performance monitor
        
        Args:
            interval: Sampling interval in seconds
        """
        self.interval = interval
        self.metrics_history: List[SystemMetrics] = []
        self.monitoring = False
        self._initial_disk_io = None
        self._initial_network_io = None
    
    def start_monitoring(self):
        """Start collecting metrics"""
        self.monitoring = True
        self._initial_disk_io = psutil.disk_io_counters()
        self._initial_network_io = psutil.net_io_counters()
        print(f"Performance monitoring started (interval: {self.interval}s)")
    
    def stop_monitoring(self):
        """Stop collecting metrics"""
        self.monitoring = False
        print("Performance monitoring stopped")
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        if self._initial_disk_io:
            disk_read_mb = (disk_io.read_bytes - self._initial_disk_io.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self._initial_disk_io.write_bytes) / (1024 * 1024)
        else:
            disk_read_mb = 0
            disk_write_mb = 0
        
        # Network I/O metrics
        network_io = psutil.net_io_counters()
        if self._initial_network_io:
            network_sent_mb = (network_io.bytes_sent - self._initial_network_io.bytes_sent) / (1024 * 1024)
            network_recv_mb = (network_io.bytes_recv - self._initial_network_io.bytes_recv) / (1024 * 1024)
        else:
            network_sent_mb = 0
            network_recv_mb = 0
        
        metrics = SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=round(memory_used_mb, 2),
            memory_available_mb=round(memory_available_mb, 2),
            disk_io_read_mb=round(disk_read_mb, 2),
            disk_io_write_mb=round(disk_write_mb, 2),
            network_sent_mb=round(network_sent_mb, 2),
            network_recv_mb=round(network_recv_mb, 2)
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_metrics_summary(self) -> Dict:
        """Get summary statistics of collected metrics"""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_percent for m in self.metrics_history]
        
        return {
            'duration_seconds': len(self.metrics_history) * self.interval,
            'samples_collected': len(self.metrics_history),
            'cpu': {
                'avg': round(sum(cpu_values) / len(cpu_values), 2),
                'max': round(max(cpu_values), 2),
                'min': round(min(cpu_values), 2)
            },
            'memory': {
                'avg': round(sum(memory_values) / len(memory_values), 2),
                'max': round(max(memory_values), 2),
                'min': round(min(memory_values), 2)
            },
            'disk_io': {
                'total_read_mb': round(sum(m.disk_io_read_mb for m in self.metrics_history), 2),
                'total_write_mb': round(sum(m.disk_io_write_mb for m in self.metrics_history), 2)
            },
            'network_io': {
                'total_sent_mb': round(sum(m.network_sent_mb for m in self.metrics_history), 2),
                'total_recv_mb': round(sum(m.network_recv_mb for m in self.metrics_history), 2)
            }
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'summary': self.get_metrics_summary(),
            'metrics': [asdict(m) for m in self.metrics_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Metrics exported to {filepath}")
    
    def print_current_metrics(self):
        """Print current system metrics"""
        metrics = self.collect_metrics()
        print(f"\n[{metrics.timestamp}]")
        print(f"CPU: {metrics.cpu_percent}%")
        print(f"Memory: {metrics.memory_percent}% ({metrics.memory_used_mb} MB used)")
        print(f"Disk I/O: Read {metrics.disk_io_read_mb} MB, Write {metrics.disk_io_write_mb} MB")
        print(f"Network: Sent {metrics.network_sent_mb} MB, Recv {metrics.network_recv_mb} MB")


def monitor_test_execution(duration_seconds: int, interval: int = 5):
    """
    Monitor system metrics during test execution
    
    Args:
        duration_seconds: How long to monitor
        interval: Sampling interval in seconds
    """
    monitor = PerformanceMonitor(interval=interval)
    monitor.start_monitoring()
    
    try:
        elapsed = 0
        while elapsed < duration_seconds:
            monitor.print_current_metrics()
            time.sleep(interval)
            elapsed += interval
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    finally:
        monitor.stop_monitoring()
        summary = monitor.get_metrics_summary()
        print("\n=== Monitoring Summary ===")
        print(json.dumps(summary, indent=2))
        
        return monitor


if __name__ == '__main__':
    # Test monitoring for 30 seconds
    print("Starting performance monitoring test...")
    monitor = monitor_test_execution(duration_seconds=30, interval=5)
    monitor.export_metrics('performance-testing/reports/test_metrics.json')
