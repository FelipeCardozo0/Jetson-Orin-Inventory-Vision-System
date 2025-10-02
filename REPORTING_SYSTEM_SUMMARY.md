# YOLOv8 Automated Monthly Reporting System - Complete Summary

## 🎯 What This System Does

This automated reporting system tracks your inventory over time and automatically sends you a detailed monthly performance report via email. It runs completely autonomously once set up.

### Key Features

✅ **Continuous Data Logging** - Every detection is saved to a database  
✅ **Automatic Monthly Reports** - Generated and emailed on the 1st of each month  
✅ **Detailed Analytics** - Sales, restocking, averages, and stock levels  
✅ **CSV Format** - Easy to open in Excel, Google Sheets, or any spreadsheet app  
✅ **Email Delivery** - Report automatically sent to your inbox  
✅ **Hands-Free Operation** - No manual intervention required  

---

## 📦 Files Delivered

### Core System Files

| File | Purpose | Status |
|------|---------|--------|
| `main_with_logging.py` | Enhanced main script with SQLite logging | ✅ Ready to use |
| `report_generator.py` | Monthly report generator | ✅ Ready to use |
| `notify_enhanced.py` | Enhanced email module with CSV support | ✅ Ready to use |

### Setup & Documentation

| File | Purpose | Status |
|------|---------|--------|
| `setup_automation.sh` | Automated setup script (bash) | ✅ Executable |
| `AUTOMATION_GUIDE.md` | Comprehensive setup guide | 📖 Reference |
| `CRON_SETUP.txt` | Quick reference for cron setup | 📖 Reference |
| `requirements-reporting.txt` | Python dependencies | 📦 Install file |
| `REPORTING_SYSTEM_SUMMARY.md` | This file | 📋 Overview |

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run the Setup Script

```bash
chmod +x setup_automation.sh
./setup_automation.sh
```

This will:
- Install Python dependencies (`python-dateutil`)
- Configure your email settings
- Set up the cron job for automatic monthly reports
- Optionally test the system

### Step 2: Start the Enhanced Main Script

Replace your current `main.py` with the logging-enabled version:

```bash
# Run with display
python3 main_with_logging.py

# Or run headless (recommended for Raspberry Pi)
python3 main_with_logging.py --headless
```

This creates the `inventory.db` database and starts logging all detections.

### Step 3: Wait for Your First Report

The system will automatically generate and email a report at **2:00 AM on the 1st of each month**.

You can also manually generate a report anytime:
```bash
python3 report_generator.py
```

---

## 📊 What's in the Report

Each monthly report includes a CSV file with these metrics for every tracked item:

### Metrics Explained

| Metric | Description | Example |
|--------|-------------|---------|
| **Total Consumed (Sales)** | Units sold/consumed during the month | 45 units |
| **Total Restocked** | Units added to inventory during the month | 50 units |
| **Average Stock Level** | Average count throughout the month | 8.5 units |
| **End of Month Stock** | Final count at month end | 12 units |

### Sample Report

```csv
Item Name,Total Consumed (Sales),Total Restocked,Average Stock Level,End of Month Stock
Cantaloupe,45,50,8.5,12
Mango,38,40,6.2,8
Pineapple,52,55,9.1,10
Sprite,67,70,11.3,15
```

---

## 🔧 Technical Details

### Database Schema

```sql
CREATE TABLE inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    item_name TEXT NOT NULL,
    item_count INTEGER NOT NULL
);
```

### Cron Schedule

```bash
# Runs at 2:00 AM on the 1st of every month
0 2 1 * * cd /your/project/path && python3 report_generator.py >> report_cron.log 2>&1
```

### Email Configuration

The system uses environment variables for email credentials:

```bash
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="465"
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"        # Gmail App Password required!
NOTIFY_FROM="your-email@gmail.com"
NOTIFY_TO="recipient@example.com"
```

**Important for Gmail Users:**  
You must use an "App Password" instead of your regular password. Generate one at:  
**Google Account → Security → 2-Step Verification → App Passwords**

---

## 📋 How It Works

### 1. Continuous Logging Phase

```
┌─────────────────────────────────────────┐
│  main_with_logging.py                   │
│  ├─ Captures video frame                │
│  ├─ Runs YOLOv8 inference                │
│  ├─ Calculates stable counts             │
│  └─ Logs to inventory.db                 │
│     • timestamp: 2025-10-15 14:23:45     │
│     • item_name: "Cantaloupe"            │
│     • item_count: 8                      │
└─────────────────────────────────────────┘
        │
        │ Logs every 5 seconds (configurable)
        │
        ▼
┌─────────────────────────────────────────┐
│  inventory.db (SQLite)                   │
│  ┌─────────────────────────────────────┐ │
│  │ 2025-10-01 08:00:00 | Mango    | 10 │ │
│  │ 2025-10-01 08:00:05 | Mango    | 10 │ │
│  │ 2025-10-01 08:00:10 | Mango    |  9 │ │ ← Sale detected!
│  │ 2025-10-01 08:00:15 | Mango    |  9 │ │
│  │ ...                                  │ │
│  │ 2025-10-15 14:00:00 | Mango    | 15 │ │ ← Restock detected!
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 2. Monthly Report Generation

```
┌─────────────────────────────────────────┐
│  Cron Job (1st of month @ 2:00 AM)      │
│  Triggers: report_generator.py          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  report_generator.py                     │
│  ├─ Connects to inventory.db             │
│  ├─ Queries past month's data            │
│  ├─ Calculates metrics:                  │
│  │   • Total consumed (↓ decreases)     │
│  │   • Total restocked (↑ increases)    │
│  │   • Average stock level              │
│  │   • End of month stock               │
│  ├─ Generates CSV file                   │
│  └─ Calls send_email()                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  notify_enhanced.py                      │
│  └─ Sends email with CSV attachment      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  📧 Your Inbox                           │
│  Subject: "Monthly Inventory Performance │
│           Report - October 2025"         │
│  Attachment: inventory_report_2025-      │
│             october.csv                  │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing the System

### Test 1: Verify Database Logging

```bash
# Start the main script
python3 main_with_logging.py

# In another terminal, check the database
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"
sqlite3 inventory.db "SELECT * FROM inventory_log ORDER BY timestamp DESC LIMIT 10;"
```

You should see records being added every few seconds.

### Test 2: Generate a Test Report

```bash
# Generate report for current month
python3 report_generator.py --month $(date +%Y-%m)
```

Check for:
- ✅ CSV file created (`inventory_report_YYYY-MONTH.csv`)
- ✅ Email received in your inbox
- ✅ No errors in `report_generator.log`

### Test 3: Verify Cron Job

```bash
# List your cron jobs
crontab -l

# You should see:
# 0 2 1 * * cd /your/path && python3 report_generator.py >> report_cron.log 2>&1
```

### Test 4: Email Configuration

```bash
python3 -c "from notify_enhanced import send_email; send_email('Test Subject', 'Test body', None)"
```

You should receive a test email.

---

## 🔍 Monitoring & Logs

### Log Files

| Log File | Contains | View Command |
|----------|----------|--------------|
| `inventory_events.log` | Low stock alerts, restocking events | `tail -f inventory_events.log` |
| `report_generator.log` | Report generation details | `tail -f report_generator.log` |
| `report_cron.log` | Cron execution output | `tail -f report_cron.log` |

### Health Checks

```bash
# Check database size
du -h inventory.db

# Count total records
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"

# View most recent entries
sqlite3 inventory.db "SELECT * FROM inventory_log ORDER BY timestamp DESC LIMIT 5;"

# Check cron service status
sudo service cron status
```

---

## 🐛 Troubleshooting

### Problem: No email received

**Solutions:**
1. Check email credentials in `~/.bashrc`
2. For Gmail, ensure you're using an App Password
3. Check spam/junk folder
4. View logs: `cat report_generator.log`
5. Test manually: `python3 report_generator.py`

### Problem: Database not found

**Solutions:**
1. Run `main_with_logging.py` first to create the database
2. Check current directory: `ls -la inventory.db`
3. Verify permissions: `ls -l inventory.db`

### Problem: Cron job not running

**Solutions:**
1. Check cron service: `sudo service cron status`
2. Use absolute paths in crontab, not relative paths
3. Verify script is executable: `chmod +x report_generator.py`
4. Check cron log: `cat report_cron.log`
5. Test the command manually from the crontab

### Problem: Empty report / No data

**Solutions:**
1. Verify `main_with_logging.py` has been running
2. Check database has data: `sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"`
3. Ensure correct month is specified
4. View report_generator.log for details

---

## 📁 Project Structure

After setup, your project should look like this:

```
your-project-directory/
├── main_with_logging.py          ← Run this as your main script
├── report_generator.py            ← Generates monthly reports
├── notify_enhanced.py             ← Email with CSV attachments
├── config.yaml                    ← Your configuration
├── best.pt                        ← Your YOLOv8 model
│
├── inventory.db                   ← SQLite database (auto-created)
│
├── inventory_report_2025-october.csv    ← Generated reports
├── inventory_report_2025-november.csv
├── inventory_report_2025-december.csv
│
├── inventory_events.log           ← Event logs
├── report_generator.log           ← Report generation logs
├── report_cron.log               ← Cron execution logs
│
├── setup_automation.sh           ← Setup script
├── AUTOMATION_GUIDE.md          ← Full documentation
├── CRON_SETUP.txt               ← Quick cron reference
└── REPORTING_SYSTEM_SUMMARY.md  ← This file
```

---

## 🎓 Understanding the Metrics

### Example Scenario

Let's say for "Mango" during October:

**Database records:**
```
2025-10-01 08:00:00 | Mango | 10
2025-10-01 12:00:00 | Mango |  8  ← 2 sold
2025-10-01 16:00:00 | Mango |  7  ← 1 sold
2025-10-02 08:00:00 | Mango | 15  ← 8 restocked
2025-10-02 12:00:00 | Mango | 13  ← 2 sold
...
2025-10-31 23:59:59 | Mango | 12  ← End of month
```

**Calculated metrics:**
- **Total Consumed:** 2 + 1 + 2 + ... = 45 units sold
- **Total Restocked:** 8 + ... = 50 units added
- **Average Stock Level:** Mean of all counts = 8.5 units
- **End of Month Stock:** Last recorded value = 12 units

---

## 🔐 Security Best Practices

1. **Never commit credentials** to version control
   ```bash
   echo ".env" >> .gitignore
   echo "inventory.db" >> .gitignore
   ```

2. **Use App Passwords** for Gmail (not your main password)

3. **Secure your database**
   ```bash
   chmod 600 inventory.db
   ```

4. **Backup regularly**
   ```bash
   # Add to crontab for daily backups at 3 AM
   0 3 * * * cp /path/to/inventory.db /path/to/backups/inventory_$(date +\%Y\%m\%d).db
   ```

---

## 📈 Future Enhancements

Potential additions you could implement:

- **Web Dashboard:** Real-time visualization of inventory
- **Weekly Reports:** More frequent reporting
- **Alerts:** Email when specific items are frequently low
- **Analytics:** Trend analysis, seasonality detection
- **Integration:** Connect to POS or ordering systems
- **Multi-location:** Support for multiple stores/locations

---

## ✅ Checklist

Use this checklist to ensure everything is set up correctly:

- [ ] `python-dateutil` installed
- [ ] Email credentials configured in `~/.bashrc`
- [ ] Gmail App Password generated (if using Gmail)
- [ ] `notify.py` updated or `notify_enhanced.py` in place
- [ ] `main_with_logging.py` tested and running
- [ ] `inventory.db` created and receiving data
- [ ] Cron job added to crontab
- [ ] Test report generated successfully
- [ ] Test email received
- [ ] Log files created and writable
- [ ] Documentation reviewed

---

## 📞 Support Resources

- **Full Setup Guide:** See `AUTOMATION_GUIDE.md`
- **Cron Reference:** See `CRON_SETUP.txt`
- **Check Logs:** `tail -f report_generator.log`
- **Database Query:** `sqlite3 inventory.db`

---

## 🎉 Conclusion

You now have a fully automated inventory reporting system that:

1. ✅ Logs all detections to a database
2. ✅ Calculates comprehensive performance metrics
3. ✅ Generates professional CSV reports
4. ✅ Emails reports automatically every month
5. ✅ Runs completely hands-free

**Set it and forget it!** The system will take care of tracking and reporting your inventory performance automatically.

---

**Version:** 1.0  
**Created:** October 2025  
**License:** For use with YOLOv8 Inventory Detection System

