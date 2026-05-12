#!/usr/bin/env python3
"""
Inference Service Dashboard
Manages multiple llama.cpp services with web UI
"""

import os
import sys
import json
from pathlib import Path

# Add venv to path if it exists
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

from flask import Flask, render_template, jsonify, request
import subprocess
import psutil
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')

# Service definitions
SERVICES = {
    'qwen3.5-4b': {'desc': 'Qwen3.5 4B (3090:8GB)', 'port': 8087},
    'qwen3.5-9b': {'desc': 'Qwen3.5 9B (3090:16GB)', 'port': 8088},
    'qwen3-14b': {'desc': 'Qwen3 14B (3090:24GB)', 'port': 8089},
    'qwen3.6-27b': {'desc': 'Qwen3.6 27B (3090+P4)', 'port': 8092},
    'gpt-oss-20b': {'desc': 'GPT-OSS 20B (3090+P4)', 'port': 8091},
}

# Data collector paths
DATA_DIR = Path.home() / 'inference-dashboard' / 'data'
METRICS_FILE = DATA_DIR / 'metrics.jsonl'

def get_service_status(name):
    """Check if service is active"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', name],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == 'active'
    except Exception as e:
        return False

def get_service_logs(name, lines=50):
    """Get recent logs from service"""
    try:
        result = subprocess.run(
            ['journalctl', '-u', name, '-n', str(lines), '--no-pager'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout or "No logs found"
    except Exception as e:
        return f"Error: {str(e)}"

def get_gpu_memory():
    """Get NVIDIA GPU memory info"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv'],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split('\n')
        gpu_info = []
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                used = parts[0].strip()
                total = parts[1].strip()
                gpu_info.append({
                    'used': int(used.replace('MiB', '')),
                    'total': int(total.replace('MiB', ''))
                })
        return gpu_info
    except Exception as e:
        return [{'error': str(e)}]

def execute_command(cmd):
    """Execute systemctl command"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        return {'success': False, 'output': '', 'error': str(e)}

def check_data_collector():
    """Check if data collector is running"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'data-collector'],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def get_data_collector_status():
    """Get data collector logs"""
    try:
        result = subprocess.run(
            ['journalctl', '-u', 'data-collector', '-n', '10', '--no-pager'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout if result.stdout else "No logs found"
    except Exception as e:
        return f"Error: {str(e)}"

def get_available_reports():
    """Get list of available reports"""
    reports_dir = Path.home() / 'inference-dashboard' / 'reports'
    if not reports_dir.exists():
        return []
    
    reports = []
    for file in reports_dir.glob('*.png'):
        timestamp = file.stem.split('_')[-1]
        reports.append({
            'name': file.name,
            'timestamp': timestamp,
            'size': file.stat().st_size
        })
    
    return sorted(reports, key=lambda x: x['timestamp'], reverse=True)[:10]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reports/')
def reports():
    """Show all available reports"""
    reports = get_available_reports()
    return render_template('reports.html', reports=reports)

@app.route('/data_collector_status/')
def data_collector_status():
    """Show data collector status"""
    is_running = check_data_collector()
    logs = get_data_collector_status()
    metrics_count = 0
    
    if METRICS_FILE.exists():
        metrics_count = sum(1 for _ in open(METRICS_FILE))
    
    return render_template('collector_status.html', 
                         is_running=is_running, 
                         logs=logs, 
                         metrics_count=metrics_count)

@app.route('/api/services')
def list_services():
    """Get status of all services"""
    services = []
    for name, config in SERVICES.items():
        status = get_service_status(name)
        services.append({
            'name': name,
            'description': config['desc'],
            'port': config['port'],
            'status': 'running' if status else 'stopped',
            'active': status
        })
    return jsonify(services)

@app.route('/api/services/<name>/status')
def service_status(name):
    """Get status of specific service"""
    status = get_service_status(name)
    return jsonify({'active': status, 'status': 'running' if status else 'stopped'})

@app.route('/api/services/<name>/logs')
def service_logs(name):
    """Get logs of specific service"""
    logs = get_service_logs(name)
    return jsonify({'logs': logs})

@app.route('/api/services/<name>/gpu')
def service_gpu(name):
    """Get GPU memory info"""
    gpu = get_gpu_memory()
    return jsonify({'gpu': gpu})

@app.route('/api/services/<name>/toggle', methods=['POST'])
def toggle_service(name):
    """Start/stop service"""
    if not name in SERVICES:
        return jsonify({'error': 'Unknown service'}), 404
    
    if request.json.get('action') == 'start':
        cmd = ['sudo', 'systemctl', 'start', name]
    elif request.json.get('action') == 'stop':
        cmd = ['sudo', 'systemctl', 'stop', name]
    elif request.json.get('action') == 'restart':
        cmd = ['sudo', 'systemctl', 'restart', name]
    else:
        return jsonify({'error': 'Unknown action'}), 400
    
    result = execute_command(cmd)
    return jsonify({
        'success': result['success'],
        'output': result['output'],
        'error': result['error']
    })

@app.route('/api/system')
def system_info():
    """Get system info"""
    try:
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            'cpu_count': cpu_count,
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/system/gpu')
def system_gpu():
    """Get all GPU info"""
    return jsonify({'gpu': get_gpu_memory()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
