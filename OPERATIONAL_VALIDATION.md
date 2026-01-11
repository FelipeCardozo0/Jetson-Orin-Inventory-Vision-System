# Operational Validation Checklist

## Database Safety

### WAL Mode Enabled
```bash
sqlite3 data/inventory.db "PRAGMA journal_mode;"
# Expected output: wal
```

**Status:** Implemented in persistence.py
**Purpose:** Enables better concurrency and crash recovery
**Verification:** Check on first run after deployment

### Synchronous Mode
```bash
sqlite3 data/inventory.db "PRAGMA synchronous;"
# Expected output: 1 (NORMAL)
```

**Status:** Implemented in persistence.py
**Purpose:** Safe with WAL mode, prevents blocking
**Verification:** Automatic on connection

### Single Writer Guarantee
```bash
# Check for PID file
ls -l /tmp/pokebowl.pid

# Verify only one instance running
ps aux | grep "python3.*main.py" | grep -v grep
```

**Status:** Implemented in main.py with PID file protection
**Purpose:** Prevents database corruption from concurrent writes
**Verification:** Attempt to start second instance (should fail)

---

## Retention Cleanup

### Automatic Cleanup on Startup
**Status:** Implemented in persistence.py `_run_startup_maintenance()`
**Default:** 30 days retention
**Behavior:**
- Deletes inventory_snapshots older than 30 days (keeps last 100)
- Deletes alerts_log older than 30 days (keeps last 100)
- Runs once on application startup
- Non-blocking, logs warnings on failure

### Verify Retention Working
```bash
# Check snapshot count before restart
sqlite3 data/inventory.db "SELECT COUNT(*) FROM inventory_snapshots;"

# Restart application
sudo systemctl restart pokebowl-inventory

# Check logs for cleanup message
sudo journalctl -u pokebowl-inventory | grep "Startup maintenance"

# Verify old records removed
sqlite3 data/inventory.db "SELECT COUNT(*) FROM inventory_snapshots;"
```

### Manual Cleanup (if needed)
```python
from backend.persistence import PersistenceManager

pm = PersistenceManager()
deleted = pm.cleanup_old_data(days_to_keep=7) # More aggressive
print(f"Deleted: {deleted}")
```

---

## Systemd Single Instance

### Service File Protection
**File:** `deployment/pokebowl-inventory.service`

**Settings:**
- `PIDFile=/tmp/pokebowl.pid` - Systemd tracks PID
- `KillMode=mixed` - Clean shutdown
- `KillSignal=SIGTERM` - Graceful termination
- `TimeoutStopSec=30` - Allow time for cleanup

### Verification
```bash
# Start service
sudo systemctl start pokebowl-inventory

# Check status
sudo systemctl status pokebowl-inventory

# Verify PID file exists
cat /tmp/pokebowl.pid

# Attempt second start (should fail or restart existing)
sudo systemctl start pokebowl-inventory

# Check only one process
ps aux | grep "python3.*main.py" | grep -v grep | wc -l
# Expected: 1
```

---

## Non-Blocking Database Writes

### Connection Timeout
**Setting:** `sqlite3.connect(timeout=10.0)`
**Purpose:** Prevents indefinite blocking
**Location:** persistence.py `_get_connection()`

### Transaction Safety
**Implementation:**
- All writes use context managers
- Automatic rollback on error
- Commit only on success
- Connection closed in finally block

### Verification
```bash
# Monitor logs during operation
tail -f /tmp/pokebowl_inventory.log | grep -E "Database|transaction"

# Should NOT see:
# - "Database locked" errors
# - Transaction timeouts
# - Blocking warnings

# Should see:
# - "Snapshot saved" (every 5 seconds)
# - "Sale attributed" (when sales occur)
# - "Alert logged" (when alerts trigger)
```

### Performance Check
```bash
# Monitor FPS during database writes
tail -f /tmp/pokebowl_inventory.log | grep "fps"

# FPS should remain 16-20 consistently
# No drops during database operations
```

---

## Database Growth Monitoring

### Check Database Size
```bash
# Current size
du -h data/inventory.db

# With WAL files
du -h data/inventory.db*
```

### Expected Growth Rates

**Conservative Estimates (30-day retention):**

| Table | Records/Day | Size/Record | Daily Growth | 30-Day Total |
|-------|-------------|-------------|--------------|--------------|
| inventory_snapshots | 17,280 | 150-300 bytes | 2.5-5 MB | 75-150 MB |
| sales_log | 50-200 | 120 bytes | 6-24 KB | 180-720 KB |
| alerts_log | 5-20 | 150 bytes | 0.75-3 KB | 22-90 KB |
| **Total** | - | - | **2.5-5 MB** | **75-150 MB** |

**Notes:**
- Actual size depends on inventory JSON complexity
- More products = larger inventory_json
- Retention cleanup keeps database bounded
- WAL files add ~10-20% overhead

### Monitor Growth
```bash
# Weekly check
ls -lh data/inventory.db

# If exceeding 200 MB, reduce retention:
# Edit persistence.py: _run_startup_maintenance(retention_days=14)
```

---

## Deployment Validation Sequence

### 1. Pre-Deployment
```bash
# Verify configuration
grep -A 3 "inventory:" config/config.yaml

# Check dependencies
pip3 list | grep -E "pytz|aiohttp|ultralytics"

# Verify model file
ls -lh best.pt
```

### 2. First Startup
```bash
# Start service
sudo systemctl start pokebowl-inventory

# Watch initialization
sudo journalctl -u pokebowl-inventory -f

# Expected log sequence:
# 1. "Configuration loaded"
# 2. "Persistence manager initialized"
# 3. "Database schema initialized successfully"
# 4. "Startup maintenance: deleted X old snapshots"
# 5. "Camera initialized"
# 6. "Detector initialized"
# 7. "Inventory tracker initialized with persistence"
# 8. "Sales attribution engine initialized"
# 9. "Web server initialized"
# 10. "System ready!"
```

### 3. Operational Checks
```bash
# Verify PID file
cat /tmp/pokebowl.pid

# Check database created
ls -l data/inventory.db*

# Verify WAL mode
sqlite3 data/inventory.db "PRAGMA journal_mode;"

# Check web interface
curl http://localhost:8080/health

# Monitor for 60 seconds
tail -f /tmp/pokebowl_inventory.log
```

### 4. Restart Test
```bash
# Restart service
sudo systemctl restart pokebowl-inventory

# Verify no duplicate instances
ps aux | grep "python3.*main.py" | grep -v grep | wc -l

# Check state restoration
sudo journalctl -u pokebowl-inventory | grep "Restored inventory"

# Verify cleanup ran
sudo journalctl -u pokebowl-inventory | grep "Startup maintenance"
```

### 5. Performance Validation
```bash
# Run for 5 minutes, monitor FPS
sudo journalctl -u pokebowl-inventory -f | grep "fps"

# Check database writes not blocking
# FPS should stay 16-20 consistently

# Verify database size reasonable
du -h data/inventory.db
```

---

## Troubleshooting

### Database Locked Errors
**Symptom:** "database is locked" in logs
**Cause:** Multiple instances or WAL not enabled
**Fix:**
```bash
# Kill all instances
pkill -f "python3.*main.py"

# Remove PID file
rm /tmp/pokebowl.pid

# Restart
sudo systemctl start pokebowl-inventory
```

### PID File Stale
**Symptom:** "Another instance already running" but no process
**Cause:** Unclean shutdown left PID file
**Fix:**
```bash
# Check if process actually running
cat /tmp/pokebowl.pid
ps -p $(cat /tmp/pokebowl.pid)

# If not running, remove PID file
rm /tmp/pokebowl.pid

# Restart
sudo systemctl start pokebowl-inventory
```

### Database Growing Too Large
**Symptom:** database.db > 500 MB
**Cause:** Retention too long or not running
**Fix:**
```bash
# Manual cleanup
python3 -c "
from backend.persistence import PersistenceManager
pm = PersistenceManager()
pm.cleanup_old_data(days_to_keep=7)
"

# Reduce retention permanently
# Edit persistence.py line: _run_startup_maintenance(retention_days=14)
```

### WAL Files Not Checkpointing
**Symptom:** inventory.db-wal growing large
**Cause:** Long-running transactions or no checkpoints
**Fix:**
```bash
# Manual checkpoint
sqlite3 data/inventory.db "PRAGMA wal_checkpoint(TRUNCATE);"

# Restart service to force checkpoint
sudo systemctl restart pokebowl-inventory
```

---

## Summary Checklist

- [ ] WAL mode enabled and verified
- [ ] Single instance protection working (PID file)
- [ ] Retention cleanup runs on startup
- [ ] No "database locked" errors in logs
- [ ] FPS remains 16-20 during database writes
- [ ] Database size grows predictably (~2-5 MB/day)
- [ ] Restart preserves state (inventory, freshness, sales)
- [ ] No duplicate processes after restart
- [ ] Web interface accessible at http://localhost:8080
- [ ] Logs show clean startup sequence

**All checks passing = System operationally safe for production**
