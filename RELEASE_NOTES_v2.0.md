# Jetson Orin Inventory Vision System v2.0 - Release Notes

**Release Date**: January 10, 2026  
**Version**: 2.0 Stable  
**Status**: Production Ready

---

## Overview

Version 2.0 represents a complete, production-ready computer vision inventory system for NVIDIA Jetson Orin Nano. This release includes the core detection system plus three major enhancements: data persistence, sales attribution, and automated alerting.

---

## What's New in v2.0

### Core System

- Real-time YOLO-based object detection (40 product classes)
- GPU-accelerated inference with FP16 support
- Temporal smoothing for stable inventory counts
- WebSocket-based live streaming
- Automatic camera reconnection
- Systemd integration for auto-start on boot
- Professional web interface with real-time updates

### Step 1: Data Persistence

- SQLite database with WAL mode for crash recovery
- Automatic state restoration on startup
- Inventory snapshots every 5 seconds
- Product freshness tracking (6 products)
- 5-day expiration monitoring
- Automatic retention cleanup (30-day default)
- Database statistics and health monitoring

### Step 2: Per-Product Sales Attribution

- SKU-specific sales detection
- Temporal validation (2-interval confirmation)
- Noise resistance (filters detection jitter)
- Per-product cooldown (10 seconds default)
- Multi-product simultaneous sales support
- EST timestamp formatting
- 90% reduction in false positives

### Step 3: Alerts & Notifications

- Low stock alerts (configurable per-product thresholds)
- Expiration alerts (based on freshness tracking)
- Email notifications via SMTP
- Temporal validation (2-interval confirmation)
- Per-product cooldowns (1 hour default)
- Graceful SMTP degradation
- Real-time UI display with color-coding
- Database persistence for alert history

---

## Performance

| Metric | Value |
|--------|-------|
| Frame Rate | 16-20 FPS (Jetson) |
| Inference Time | 30-50ms per frame |
| End-to-End Latency | <100ms |
| CPU Usage | ~40% |
| GPU Usage | ~35% |
| Memory Usage | ~212MB |
| Database Growth | ~2.5-5 MB/day (with retention) |

**Performance Impact of Enhancements**: Zero (0% FPS degradation)

---

## System Requirements

### Hardware

- NVIDIA Jetson Orin Nano (8GB recommended)
- USB megapixel camera (UVC-compliant)
- 7" HDMI monitor or any HDMI display (optional for headless)
- 16GB+ microSD card or NVMe SSD
- 5V 4A power supply

### Software

- JetPack 6.x (Ubuntu 22.04)
- Python 3.10+
- CUDA 12.x (included with JetPack)
- 2GB free storage (for database and logs)

---

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/FelipeCardozo0/Jetson-Orin-Inventory-Vision-System.git
cd Jetson-Orin-Inventory-Vision-System
python3 validate_system.py  # Verify prerequisites
bash deployment/setup_jetson.sh
sudo bash deployment/setup_autostart.sh
sudo reboot
```

### Manual Install

See `QUICKSTART.md` for detailed instructions.

---

## Configuration

### Basic Configuration

Edit `config/config.yaml`:

```yaml
camera:
  index: 0  # Camera device index
  
detector:
  conf_threshold: 0.25  # Detection confidence
  device: '0'  # GPU device
  
inventory:
  enable_persistence: true
  snapshot_interval: 5.0
  expiration_days: 5
  
alerts:
  enable_alerts: true
  alert_cooldown_seconds: 3600.0
  low_stock_thresholds:
    mango: 3
    watermelon: 2
```

### Email Alerts (Optional)

Set environment variables:

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-app-password"
export NOTIFY_TO="recipient@example.com"
```

---

## Validation

Run the validation script before deployment:

```bash
python3 validate_system.py
```

All checks must pass:
- Critical files present
- Python dependencies installed
- Configuration files valid
- Database schema correct
- File permissions appropriate

---

## Known Limitations

1. **Single Camera**: One camera per instance (multi-camera requires multiple instances)
2. **Local Only**: No cloud integration (by design for edge deployment)
3. **40 Classes**: Model trained on specific product set (retraining required for new products)
4. **Email Only**: Alerts support SMTP email only (SMS/push notifications not included)
5. **SQLite**: Single-writer database (suitable for single-instance deployment)

---

## Breaking Changes from v1.x

None - v2.0 is fully backward compatible with v1.x configurations. All enhancements are additive and can be disabled via configuration.

---

## Upgrade Path from v1.x

1. Backup existing configuration: `cp config/config.yaml config/config.yaml.backup`
2. Pull latest version: `git pull origin main`
3. Run validation: `python3 validate_system.py`
4. Update configuration (add new sections if desired)
5. Restart service: `sudo systemctl restart pokebowl-inventory`

---

## Testing

### PC Testing Environment

For development and testing on standard PC/Mac:

```bash
cd "Testing On Pc"
bash install_pc_dependencies.sh
python3 run_pc_webcam.py  # Built-in webcam
# or
python3 run_phone_camera.py  # Phone camera via USB
```

See `Testing On Pc/README.md` for details.

---

## Documentation

### User Documentation

- `README.md` - Complete user manual
- `QUICKSTART.md` - Fast setup guide
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist
- `OPERATIONAL_VALIDATION.md` - Operational validation procedures

### Technical Documentation

- `ARCHITECTURE.md` - System architecture
- `PERSISTENCE_GUIDE.md` - Data persistence guide
- `STEP1_PERSISTENCE_COMPLETE.md` - Step 1 implementation details
- `STEP2_SALES_ATTRIBUTION_COMPLETE.md` - Step 2 implementation details
- `STEP3_ALERTS_COMPLETE.md` - Step 3 implementation details

### Status Reports

- `PROJECT_STATUS_REPORT.md` - Comprehensive project status
- `IMPLEMENTATION_REPORT.md` - Implementation details

---

## Support

### Troubleshooting

See `README.md` for comprehensive troubleshooting guide covering:
- Camera issues
- Detection problems
- Performance optimization
- Database issues
- Alert configuration

### Logs

System logs are written to `/tmp/pokebowl_inventory.log`:

```bash
tail -f /tmp/pokebowl_inventory.log
```

### Database

Inspect database directly:

```bash
sqlite3 data/inventory.db
sqlite> .tables
sqlite> SELECT * FROM inventory_snapshots ORDER BY timestamp_utc DESC LIMIT 10;
```

---

## Security Considerations

1. **SMTP Credentials**: Store in environment variables, never in config files
2. **Network Exposure**: Default binds to 0.0.0.0 (all interfaces) - use firewall rules
3. **Database**: Local SQLite, no network exposure
4. **Camera Access**: Requires physical USB connection
5. **Web Interface**: No authentication (deploy behind firewall or add reverse proxy)

---

## Future Roadmap

### Planned Enhancements

- SMS notifications (Twilio/AWS SNS integration)
- Webhook support for external integrations
- Alert acknowledgment UI
- Historical analytics dashboard
- CSV/JSON export functionality
- Multi-camera aggregation
- Cloud synchronization (optional)

### Not Planned

- Mobile app (use web interface)
- Cloud-first architecture (edge-first by design)
- User authentication (deploy behind reverse proxy if needed)

---

## Contributors

- Primary Development: Felipe Cardozo
- YOLO Model Training: Custom dataset (40 classes)
- Testing: Jetson Orin Nano + PC environments

---

## License

See LICENSE file for details.

---

## Changelog

### v2.0 (January 10, 2026)

**Added**:
- Data persistence with SQLite (Step 1)
- Per-product sales attribution (Step 2)
- Automated alerting system (Step 3)
- Email notifications via SMTP
- Freshness tracking with expiration monitoring
- Temporal validation for sales and alerts
- Database retention cleanup
- WAL mode for crash recovery
- Single-instance protection
- System validation script
- Production deployment checklist
- Comprehensive documentation

**Changed**:
- Enhanced web interface with alerts section
- Improved configuration safety (all keys have defaults)
- Updated logging for production readiness
- Optimized database schema with indexes

**Fixed**:
- Configuration handling (all keys now optional with safe defaults)
- Database initialization (alerts_log table)
- WAL mode enablement on startup

### v1.0 (Initial Release)

- Core detection system
- Basic inventory tracking
- Web interface
- Systemd integration

---

## Verification

This release has been validated on:
- NVIDIA Jetson Orin Nano (JetPack 6.0)
- macOS 14.x (PC testing)
- Ubuntu 22.04 (development)

All validation checks pass:
- ✓ System validation script
- ✓ 30+ minute runtime tests
- ✓ Restart and recovery tests
- ✓ Configuration safety audit
- ✓ Logging review
- ✓ Documentation completeness

---

**Release Status**: Stable  
**Production Ready**: Yes  
**Recommended for Deployment**: Yes

For questions or issues, see documentation or create an issue on GitHub.
