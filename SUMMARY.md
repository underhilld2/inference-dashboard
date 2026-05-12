# Inference Dashboard Summary

## What Was Built

A **Dual GPU Inference Service Dashboard** for managing llama.cpp services with historical performance tracking.

## Hardware Configuration

Optimized for dual-GPU systems:
- **GTX 3090 (24GB)** - Primary GPU for 14B-22B models
- **P4 (8GB)** - Overflow for 27B+ models  
- **Xeon E5-2697 v4 (32GB RAM)** - CPU offload support

## Key Features

### 🎨 Web Dashboard
- Toggle buttons for start/stop/restart services
- Real-time status indicators (green=running, red=stopped)
- System statistics (CPU%, Memory%, GPU usage)
- Recent logs for each service
- Responsive dark theme UI

### 📊 Historical Data
- Automatic metrics collection every 60 seconds
- CPU usage tracking
- Memory usage tracking
- GPU memory per GPU
- Service availability monitoring
- Performance trend analysis

### 🖼️ Performance Reports
- Summary charts (CPU, Memory, GPU usage)
- Service availability graphs
- Per-model trend analysis
- Auto-generated PNG reports

## Files Included

### Core Application
- `app.py` - Flask backend with API endpoints
- `data_collector.py` - Metrics collection service
- `visualization.py` - Report generation with matplotlib
- `requirements.txt` - Python dependencies (flask, psutil, matplotlib, pandas)
- `deploy.sh` - Automated installation script

### Templates
- `templates/index.html` - Main dashboard UI
- `templates/reports.html` - Reports listing page
- `templates/collector_status.html` - Data collector status page

### Service Files
- `inference-dashboard.service` - Web dashboard systemd service
- `data-collector.service` - Data collection systemd service

### Model Services (5 total)
- `qwen3.5-4b.service`
- `qwen3.5-9b.service`
- `qwen3-14b.service`
- `qwen3.6-27b.service`
- `gpt-oss-20b.service`

### Launcher Script
- `ai-launcher-dualgpu.sh` - Dual-GPU model launcher (3090+P4)

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/underhilld2/inference-dashboard.git
cd inference-dashboard

# 2. Install dependencies
chmod +x deploy.sh
./deploy.sh

# 3. Start services
sudo systemctl start inference-dashboard.service
sudo systemctl start data-collector.service

# 4. Access dashboard
# http://localhost:5000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/services` | GET | List all services |
| `/api/services/<name>/status` | GET | Check service status |
| `/api/services/<name>/logs` | GET | Get service logs |
| `/api/services/<name>/toggle` | POST | Start/stop/restart |
| `/api/system` | GET | System info |
| `/api/system/gpu` | GET | GPU memory info |

## Service Management

### Start Services
```bash
sudo systemctl start inference-dashboard.service
sudo systemctl start data-collector.service
```

### Check Status
```bash
systemctl status inference-dashboard.service
systemctl status data-collector.service
```

### Enable Auto-Start
```bash
sudo systemctl enable inference-dashboard.service
sudo systemctl enable data-collector.service
```

### Stop Services
```bash
sudo systemctl stop inference-dashboard.service
sudo systemctl stop data-collector.service
```

## Data Collection

### How It Works
- Runs every 60 seconds
- Collects: CPU%, Memory%, GPU memory, service status
- Saves to `~/inference-dashboard/data/metrics.jsonl`
- Generates reports in `~/inference-dashboard/reports/`

### Generate Reports Manually
```bash
cd ~/inference-dashboard
source venv/bin/activate
python3 visualization.py
```

### View Generated Reports
```bash
ls -lh ~/inference-dashboard/reports/
```

## Performance Tips

### Optimize Data Collection
- Default interval: 60 seconds
- Adjust based on data volume needs

### Storage Management
- Metrics file grows over time
- Clean old reports regularly
- Keep last 7 days recommended

### GPU Monitoring
- Dashboard shows per-GPU memory usage
- Track usage patterns
- Identify potential memory leaks

## Troubleshooting

### Dashboard Won't Start
```bash
journalctl -u inference-dashboard -n 20
cd ~/inference-dashboard
source venv/bin/activate
python3 app.py
```

### Data Collector Not Running
```bash
sudo systemctl restart data-collector
journalctl -u data-collector -f
```

### No Metrics Being Collected
- Check if `nvidia-smi` is available
- Verify data directory permissions
- Check service status logs

### Port Already in Use
```bash
sudo lsof -i :5000
# Change PORT in app.py if needed
```

## Security Notes

### Current Setup
- No authentication (for demo/testing)
- Runs on port 5000
- Accessible to all network interfaces

### For Production
1. Add authentication to `app.py`
2. Use HTTPS with reverse proxy
3. Restrict access by IP
4. Configure firewall rules

### Example Firewall Rule
```bash
sudo ufw allow from YOUR_IP to any port 5000
```

## Deployment Checklist

- [ ] Clone repository to new server
- [ ] Run `deploy.sh` to install dependencies
- [ ] Copy service files to server
- [ ] Enable systemd services
- [ ] Start services
- [ ] Access dashboard at http://server:5000
- [ ] Verify metrics collection
- [ ] Check performance reports

## Repository Info

- **Owner:** underhilld2
- **URL:** https://github.com/underhilld2/inference-dashboard
- **License:** MIT License
- **Created:** May 2026
- **Total Files:** 11
- **Total Lines:** 1179+

## Contact

For support or questions:
- Check logs: `journalctl -u <service>`
- View data: `~/inference-dashboard/data/`
- View reports: `~/inference-dashboard/reports/`
