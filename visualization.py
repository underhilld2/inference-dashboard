#!/usr/bin/env python3
"""
Historical Performance Visualization
Reads metrics from metrics.jsonl and creates charts
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import pandas as pd
from matplotlib.gridspec import GridSpec

DATA_FILE = Path.home() / 'inference-dashboard' / 'data' / 'metrics.jsonl'
OUTPUT_DIR = Path.home() / 'inference-dashboard' / 'reports'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_metrics():
    metrics = []
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            for line in f:
                try:
                    metrics.append(json.loads(line))
                except:
                    continue
    return metrics

def get_last_n_metrics(n=100):
    metrics = load_metrics()
    return metrics[-n:] if len(metrics) > n else metrics

def create_summary_chart(metrics):
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 3, figure=fig, height_ratios=[1, 1, 2], hspace=0.3, wspace=0.2)
    
    timestamps = [m['timestamp'] for m in metrics]
    timestamps_cpu = [datetime.fromisoformat(m['timestamp']) for m in metrics]
    
    # CPU Usage
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(timestamps_cpu, [m['cpu'] for m in metrics], marker='o', linewidth=2, markersize=4)
    ax1.set_title('CPU Usage (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Percentage')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 100)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Memory Usage
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(timestamps_cpu, [m['memory'] for m in metrics], marker='s', linewidth=2, markersize=4, color='#e94560')
    ax2.set_title('Memory Usage (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Percentage')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # GPU Memory - GPU 0
    ax3 = fig.add_subplot(gs[0, 2])
    gpu0_data = [m['gpu'] for m in metrics]
    gpu0_used = [g['used'] for g in gpu0_data]
    gpu0_total = [g['total'] for g in gpu0_data]
    ax3.plot(timestamps_cpu, gpu0_used, marker='^', linewidth=2, markersize=4)
    ax3.set_title('GPU Memory Usage', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Used (MiB)')
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Summary Statistics
    ax4 = fig.add_subplot(gs[2, 0])
    stats = {'avg_cpu': sum(m['cpu'] for m in metrics) / len(metrics),
             'max_cpu': max(m['cpu'] for m in metrics),
             'avg_mem': sum(m['memory'] for m in metrics) / len(metrics),
             'max_mem': max(m['memory'] for m in metrics)}
    
    bars = ax4.bar(['Average CPU', 'Max CPU', 'Average Mem', 'Max Mem'],
                   [stats['avg_cpu'], stats['max_cpu'], stats['avg_mem'], stats['max_mem']],
                   color=['#4ade80', '#f87171', '#4ade80', '#f87171'], alpha=0.7)
    ax4.set_title('Usage Statistics', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Percentage (%)')
    ax4.set_ylim(0, 100)
    
    # Service Availability
    ax5 = fig.add_subplot(gs[2, 1])
    services = ['qwen3.5-4b', 'qwen3.5-9b', 'qwen3-14b']
    availability = []
    for i, service in enumerate(services):
        running = sum(1 for m in metrics if m.get('services', {}).get(service, {}).get('status') == 'running')
        availability.append(running / len(metrics) * 100)
    
    ax7.bar(services, availability, color=['#4ade80'] * len(availability))
    ax7.set_title('Service Availability (%)', fontsize=12, fontweight='bold')
    ax7.set_ylabel('Percentage (%)')
    ax7.set_ylim(0, 100)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = OUTPUT_DIR / f'summary_{timestamp}.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    return output_file

def create_trend_chart(metrics, service_name='qwen3-14b'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
    
    # Status trend
    ax1 = axes[0, 0]
    status_data = [m.get('services', {}).get(service_name, {}).get('status', 'stopped') for m in metrics]
    ax1.plot(timestamps, status_data, marker='o', linewidth=2, markersize=5)
    ax1.set_title(f'{service_name} Status', fontsize=12, fontweight='bold')
    ax1.set_ylim(-0.5, 1.5)
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(['stopped', 'running'])
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # CPU usage
    ax2 = axes[0, 1]
    ax2.plot(timestamps, [m['cpu'] for m in metrics], marker='s', linewidth=2, color='#60a5fa')
    ax2.set_title('CPU Usage', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Percentage (%)')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # Memory usage
    ax3 = axes[1, 0]
    ax3.plot(timestamps, [m['memory'] for m in metrics], marker='D', linewidth=2, color='#e94560')
    ax3.set_title('Memory Usage', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Percentage (%)')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 100)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # GPU memory
    ax4 = axes[1, 1]
    gpu_used = [g['used'] for g in metrics]
    ax4.plot(timestamps, gpu_used, marker='^', linewidth=2, color='#fbbf24')
    ax4.set_title('GPU Memory (GPU 0)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Used (MiB)')
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = OUTPUT_DIR / f'{service_name}_trend_{timestamp}.png'
    fig.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    return output_file

def main():
    print('Loading metrics...')
    metrics = get_last_n_metrics(100)
    
    if not metrics:
        print('No metrics found. Run data_collector.py first.')
        return
    
    print(f'Found {len(metrics)} metrics entries')
    
    print('Creating summary chart...')
    create_summary_chart(metrics)
    
    services = ['qwen3.5-4b', 'qwen3.5-9b', 'qwen3-14b', 'qwen3.6-27b', 'gpt-oss-20b']
    for service in services:
        print(f'Creating trend chart for {service}...')
        create_trend_chart(metrics, service)
    
    print('All reports generated!')
    print(f'Reports directory: {OUTPUT_DIR}')

if __name__ == '__main__':
    main()
