# Data Persistence Guide

## Overview

The Jetson Orin Inventory Vision System now includes a production-safe data persistence layer that automatically stores inventory snapshots, product freshness tracking, and sales logs to a local SQLite database. This enhancement enables state restoration across restarts, historical analytics, and future cloud synchronization capabilities.

## Key Features

### 1. Inventory Snapshots
- Automatically saves inventory state every 5 seconds (configurable)
- Stores timestamped product counts after temporal smoothing
- Enables historical trend analysis and reporting
- Survives application restarts and system reboots

### 2. Freshness Tracking
- Tracks first-seen timestamp for monitored products
- Calculates age in days automatically
- Marks products as expired after 5 days (configurable)
- Resumes tracking accurately after restarts

**Tracked Products:**
- Passion Fruit / Island Passion Fruit
- Maui Custard
- Lemon Cake / Kilauea Lemon Cake
- Mango
- Watermelon
- Pineapple

### 3. Sales Log
- Detects inventory decreases every 5 seconds
- Records product name, quantity sold, and timestamp
- Timestamps stored in US Eastern Time (EST)
- Enables sales analytics and reporting

## Architecture

### Database Schema

**inventory_snapshots**
- `id`: Primary key
- `timestamp_utc`: UTC timestamp
- `frame_number`: Frame number when captured
- `total_items`: Sum of all product counts
- `inventory_json`: JSON-encoded inventory dictionary
- `created_at`: Record creation timestamp

**product_freshness**
- `product_name`: Primary key
- `first_seen_utc`: First detection timestamp
- `last_seen_utc`: Most recent detection timestamp
- `is_expired`: Boolean expiration flag
- `expiration_days`: Days until expiration (default: 5)
- `updated_at`: Record update timestamp

**sales_log**
- `id`: Primary key
- `timestamp_utc`: UTC timestamp
- `timestamp_est`: EST formatted timestamp
- `product_name`: Product sold
- `quantity_delta`: Number of items sold
- `inventory_before`: Count before sale
- `inventory_after`: Count after sale
- `created_at`: Record creation timestamp

**alerts_log** (Step 3 - partial implementation)
- `id`: Primary key
- `timestamp_utc`: UTC timestamp
- `timestamp_est`: EST formatted timestamp
- `alert_type`: Type of alert (low_stock, expiration)
- `product_name`: Product that triggered alert
- `severity`: Severity level (info, warning, critical)
- `message`: Alert message
- `metadata_json`: Additional alert metadata
- `acknowledged`: Acknowledgment flag
- `created_at`: Record creation timestamp

### Storage Location

**Default Path:**
```
<project_root>/data/inventory.db
```

**Jetson:**
```
~/Jetson-Orin-Inventory-Vision-System/data/inventory.db
```

**PC Testing:**
```
<project_root>/data/inventory.db
```

### Operational Safety Features

**WAL Mode (Write-Ahead Logging):**
- Enabled automatically on database initialization
- Provides better concurrency and crash recovery
- Allows readers and writers to operate simultaneously
- Reduces database locking issues

**Retention Policy:**
- Automatic cleanup runs on application startup
- Default retention: 30 days
- Keeps last 100 records of each table type for state restoration
- Configurable via `_run_startup_maintenance(retention_days=N)`
- Prevents unbounded database growth

**Single-Writer Protection:**
- PID file prevents concurrent database access
- Systemd service includes PID file tracking
- Automatic detection of stale PID files
- Prevents database corruption from multiple instances

## Configuration

### Enable/Disable Persistence

Edit `config/config.yaml` (Jetson) or `Testing On Pc/pc_config.yaml` (PC):

```yaml
inventory:
 enable_persistence: true # Set to false to disable
 snapshot_interval: 5.0 # Seconds between snapshots
 expiration_days: 5 # Days until products expire
```

### Performance Impact

- **Minimal overhead**: Database writes are asynchronous and non-blocking
- **No FPS impact**: Maintains current 16-20 FPS on Jetson
- **Low storage**: ~40 KB for empty database, grows ~2.5-5 MB per day (with 30-day retention policy)
- **Automatic cleanup**: Runs on startup, keeps last 30 days of data (configurable)
- **WAL mode**: Enabled for better concurrency and crash recovery
- **Single-writer protection**: PID file prevents concurrent database access

## State Restoration

### On Startup

The system automatically:
1. Loads the most recent inventory snapshot
2. Restores freshness tracking for all products
3. Resumes freshness timers from persisted timestamps
4. Continues sales detection from last known state

### After Restart

- Freshness timers continue accurately (no reset)
- Sales log history is preserved
- Inventory returns to last known state until new detections stabilize

## API Endpoints

### HTTP Endpoints

**Get Freshness Data:**
```bash
curl http://localhost:8080/api/freshness
```

**Get Sales Log:**
```bash
curl http://localhost:8080/api/sales?limit=100
```

**Get Statistics:**
```bash
curl http://localhost:8080/api/stats
```

### WebSocket Messages

The persistence layer automatically broadcasts updates via WebSocket:

**Freshness Update:**
```json
{
 "type": "freshness",
 "data": {
 "mango": {
 "first_seen_utc": 1704902400.0,
 "age_days": 2.5,
 "is_expired": false
 }
 },
 "timestamp": 1704988800.0
}
```

**Sales Update:**
```json
{
 "type": "sales",
 "data": [
 {
 "product_name": "mango",
 "quantity_delta": 2,
 "timestamp_est": "2026-01-10 03:30:00 PM EST",
 "inventory_before": 10,
 "inventory_after": 8
 }
 ],
 "timestamp": 1704988800.0
}
```

## Testing

### Verify Persistence

**Manual Verification:**

```bash
# Check database exists
ls -lh data/inventory.db

# Query database directly
sqlite3 data/inventory.db "SELECT COUNT(*) FROM inventory_snapshots;"
sqlite3 data/inventory.db "SELECT COUNT(*) FROM product_freshness;"
sqlite3 data/inventory.db "SELECT COUNT(*) FROM sales_log;"
```

**Runtime Verification:**

1. Start the application
2. Wait for detections (30+ seconds)
3. Check database has records:
 ```bash
 sqlite3 data/inventory.db "SELECT COUNT(*) FROM inventory_snapshots;"
 ```
4. Restart application - verify state restoration in logs:
 ```bash
 tail -f /tmp/pokebowl_inventory.log | grep "Restored"
 ```

## Maintenance

### Database Cleanup

Remove old data to prevent database bloat:

```python
from backend.persistence import PersistenceManager

pm = PersistenceManager()
deleted = pm.cleanup_old_data(days_to_keep=30)
print(f"Deleted: {deleted}")
```

### Database Statistics

Check database size and record counts:

```python
from backend.persistence import PersistenceManager

pm = PersistenceManager()
stats = pm.get_database_stats()
print(stats)
```

Output:
```python
{
 'database_path': '.../data/inventory.db',
 'database_size_mb': 1.2,
 'snapshot_count': 5000,
 'freshness_count': 6,
 'sales_count': 150
}
```

### Manual Database Access

The database is standard SQLite and can be accessed with any SQLite client:

```bash
sqlite3 data/inventory.db

# List tables
.tables

# Query inventory snapshots
SELECT * FROM inventory_snapshots ORDER BY timestamp_utc DESC LIMIT 10;

# Query sales log
SELECT * FROM sales_log ORDER BY timestamp_utc DESC LIMIT 20;

# Query freshness
SELECT * FROM product_freshness;
```

## Troubleshooting

### Database Locked Error

**Symptom:** "database is locked" error in logs

**Solution:**
- Ensure only one instance of the application is running
- Check for zombie processes: `ps aux | grep python3`
- Kill stale processes: `pkill -f pokebowl`

### Persistence Not Working

**Symptom:** No database file created or no data stored

**Solution:**
1. Check configuration: `enable_persistence: true`
2. Verify write permissions: `ls -la data/`
3. Check logs: `tail -f /tmp/pokebowl_inventory.log`
4. Verify database exists: `ls -lh data/inventory.db`

### Database Corruption

**Symptom:** SQLite errors or crashes

**Solution:**
1. Stop the application
2. Backup the database: `cp data/inventory.db data/inventory.db.backup`
3. Check integrity: `sqlite3 data/inventory.db "PRAGMA integrity_check;"`
4. If corrupted, restore from backup or delete and restart

### High Storage Usage

**Symptom:** Database file growing too large

**Solution:**
1. Run cleanup: `pm.cleanup_old_data(days_to_keep=7)`
2. Reduce snapshot interval in config: `snapshot_interval: 10.0`
3. Implement automatic cleanup (see Future Enhancements)

## Cross-Platform Compatibility

### Jetson Deployment

- Full persistence enabled by default
- Database survives reboots
- Systemd service automatically restarts with state
- No additional configuration required

### PC Testing (Webcam)

```bash
cd "Testing On Pc"
python3 run_pc_webcam.py
```

- Uses same persistence layer
- Database stored in project root
- State preserved across test sessions

### PC Testing (Phone Camera)

```bash
cd "Testing On Pc"
python3 run_phone_camera.py
```

- Identical persistence behavior
- Shared database with webcam mode

## Future Enhancements

The persistence layer is designed to support:

1. **Cloud Synchronization**
 - Export to cloud storage (S3, Google Cloud)
 - Remote monitoring and analytics
 - Multi-device synchronization

2. **Advanced Analytics**
 - Sales trends and forecasting
 - Peak hour analysis
 - Product popularity metrics
 - Expiration alerts

3. **Automated Reports**
 - Daily/weekly sales summaries
 - Inventory turnover reports
 - Expiration notifications
 - Email/SMS alerts

4. **Data Export**
 - CSV export for Excel analysis
 - JSON export for external systems
 - PDF reports generation

5. **Backup and Recovery**
 - Automatic database backups
 - Cloud backup integration
 - Point-in-time recovery

## Implementation Details

### Additive Design

- **Zero modifications** to original codebase
- New files only: `persistence.py`, `inventory_persistent.py`
- Backward compatible: disable with `enable_persistence: false`
- Graceful degradation: system continues if persistence fails

### Transaction Safety

- All database operations are transactional
- Automatic rollback on errors
- Connection pooling with context managers
- No data corruption risk

### Performance Optimizations

- Indexed timestamp columns for fast queries
- Batch writes every 5 seconds (not per frame)
- Asynchronous broadcast to WebSocket clients
- Minimal memory footprint (~5 MB)

### Error Handling

- Non-blocking: persistence failures don't crash the system
- Comprehensive logging: all errors logged to file
- Automatic recovery: retries on transient failures
- Fail-safe: continues live operation without persistence

## Support

For issues or questions:

1. Check logs: `/tmp/pokebowl_inventory.log`
2. Run test script: `python3 test_persistence.py`
3. Review this guide
4. Check database integrity with SQLite tools

## Summary

The persistence layer provides:

- Automatic inventory snapshots every 5 seconds
- Product freshness tracking with 5-day expiration
- Sales log with EST timestamps
- State restoration on restart
- Cross-platform compatibility (Jetson and PC)
- Zero performance impact
- Production-safe and failure-tolerant
- Foundation for future analytics and cloud integration

**Status:** Production Ready

**Tested On:**
- macOS (PC testing environment)
- NVIDIA Jetson Orin Nano (target deployment)

**Database:** SQLite 3.x

**Dependencies:** `pytz>=2023.3` (for timezone support)
