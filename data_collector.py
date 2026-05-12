#!/usr/bin/env python3
"""
Data Collector for Inference Dashboard
Collects performance metrics for historical analysis
"""

import os
import json
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
DATA_DIR = Path.home() / "inference-dashboard" / "data"
METRICS_FILE = DATA_DIR / "metrics.jsonl"
INTERVAL = 60  # seconds

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_gpu_memory():
    """Get NVIDIA GPU memory info"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total,name', '--format=csv'],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split('\n')
        gpu_info = []
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 3:
                gpu_info.append({
                    'name': parts[2].strip(),
                    'used': int(parts[0].replace('MiB', '')),
                    'total': int(parts[1].replace('MiB', ''))
                })
        return gpu_info
    except Exception as e:
        return [{'error': str(e)}]

def get_service_status(name):
    """Check if service is active"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', name],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def get_service_metrics(name):
    """Get metrics for a specific service"""
    try:
        # Get logs with timestamps
        result = subprocess.run(
            ['journalctl', '-u', name, '--no-pager', '-n', '5'],
            capture_output=True, text=True, timeout=10
        )
        return {
            'status': 'running' if get_service_status(name) else 'stopped',
            'logs_count': len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        }
    except:
        return {'status': 'error', 'error': 'Failed to get metrics'}

def collect_metrics():
    """Collect all metrics"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'gpu': get_gpu_memory(),
        'services': {}
    }
    
    # Collect service metrics
    services = [
        'qwen3.5-4b', 'qwen3.5-9b', 'qwen3-14b', 
        'qwen3.6-27b', 'gpt-oss-20b'
    ]
    
    for service in services:
        metrics['services'][service] = get_service_metrics(service)
    
    return metrics

def save_metrics(metrics):
    """Save metrics to JSONL file"""
    with open(METRICS_FILE, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

def main():
    """Main loop"""
    print(f"Data collector started. Saving metrics to {METRICS_FILE}")
    print(f"Collecting data every {INTERVAL} seconds...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            metrics = collect_metrics()
            save_metrics(metrics)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Collected metrics")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping data collector...")

if __name__ == '__main__':
    main()
