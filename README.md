# Dual GPU Inference Service Dashboard

A web-based dashboard for managing llama.cpp inference services with historical performance tracking.

## Features

- 🎨 **Web Dashboard** - Toggle services with simple buttons
- 📊 **Real-time Monitoring** - CPU, Memory, GPU usage
- 📈 **Historical Data** - Automatic metrics collection every 60s
- 🖼️ **Performance Reports** - Visual charts and trend analysis
- 🔧 **Service Management** - Start/Stop/Restart from web UI

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Create directories
mkdir -p data reports

# Start services
sudo systemctl start inference-dashboard.service
sudo systemctl start data-collector.service

# Access dashboard
http://localhost:5000
```

## Architecture

```
┌─────────────────────────────────────────┐
│          Web Dashboard (Flask)          │
│         :5000 / Inference UI            │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  qwen3.5-4b   │  qwen3.5-9b   │  qwen3-14b   │  gpt-oss-20b   │
│  Service     │  Service     │  Service     │  Service     │
└─────────┬───┘ └─────────┬─────┘ └─────────┬─────┘ └─────────┬─────┘
          │                │                 │                 │
          └────────────────┼─────────────────┴─────────────────┘
                           │
                    ┌──────┴──────┐
                    │ Data Collector │
                    │ (60s interval) │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ Metrics JSONL│
                    │ Reports PNG  │
                    └─────────────┘
```

## Files

- `app.py` - Flask backend with API endpoints
- `data_collector.py` - Metrics collection service
- `visualization.py` - Generate performance charts
- `templates/` - Dashboard HTML templates
- `*.service` - systemd service files

## Services

### Inference Dashboard
```bash
sudo systemctl enable inference-dashboard.service
sudo systemctl start inference-dashboard.service
```

### Data Collector
```bash
sudo systemctl enable data-collector.service
sudo systemctl start data-collector.service
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

## Configuration

Edit `app.py` to customize:
- `SERVICES` - Define service configurations
- `INTERVAL` - Metrics collection interval
- `PORT` - Web server port

## Hardware Setup

Optimized for dual-GPU systems:
- **GTX 3090 (24GB)** - Primary GPU for 14B-22B models
- **P4 (8GB)** - Overflow for 27B+ models
- **32GB RAM** - CPU offload support

## License

MIT License
