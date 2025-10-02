# Automated Monthly Reporting System - Setup Guide

This guide explains how to set up and use the automated monthly inventory reporting system for your YOLOv8 project.

## System Overview

The automated reporting system consists of three main components:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Data Logging (main_with_logging.py)                     │
│     • Runs continuously on Raspberry Pi                      │
│     • Logs all inventory detections to SQLite database       │
│     • Records: timestamp, item_name, item_count              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Report Generation (report_generator.py)                  │
│     • Runs monthly (scheduled via cron)                      │
│     • Analyzes data from database                            │
│     • Calculates metrics (sales, restocking, averages)       │
│     • Generates CSV report                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Email Delivery (notify_enhanced.py)                      │
│     • Automatically emails CSV report to owner               │
│     • Includes summary and attachment                        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Setup (Automated)

The easiest way to set up the system is using the automated setup script:

```bash
# Make the script executable
chmod +x setup_automation.sh

# Run the setup script
./setup_automation.sh
```

The script will:
1. Install required Python packages
2. Configure email settings
3. Set up the cron job for automatic monthly reports
4. Optionally run a test report

## Manual Setup

If you prefer to set up manually, follow these steps:

### Step 1: Install Dependencies

```bash
pip install python-dateutil
```

### Step 2: Configure Email Settings

Set up environment variables for email delivery. Add these to your `~/.bashrc` file:

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-app-password"
export NOTIFY_FROM="your-email@gmail.com"
export NOTIFY_TO="recipient@example.com"
```

**Important for Gmail users:**
- You need to use an "App Password" instead of your regular password
- Go to: Google Account → Security → 2-Step Verification → App Passwords
- Generate a new app password for "Mail"

After adding these variables, reload your shell:
```bash
source ~/.bashrc
```

### Step 3: Update notify.py

Replace your existing `notify.py` with `notify_enhanced.py`, or modify the `send_email` function to support CSV attachments as shown in `notify_enhanced.py`.

```bash
# Option 1: Replace notify.py
cp notify_enhanced.py notify.py

# Option 2: Keep both and import from notify_enhanced in report_generator.py
# (Already configured in the provided report_generator.py)
```

### Step 4: Start Using the Enhanced main.py

Replace your main detection script with the enhanced version:

```bash
# Run the enhanced main script with logging
python main_with_logging.py

# Or run in headless mode (no video display)
python main_with_logging.py --headless

# Use a custom database path
python main_with_logging.py --db /path/to/inventory.db
```

### Step 5: Set Up Cron Job for Automatic Reports

Open your crontab editor:
```bash
crontab -e
```

Add the following line to run the report at 2:00 AM on the 1st of every month:
```bash
0 2 1 * * cd /home/pi/your-project-directory && /usr/bin/python3 /home/pi/your-project-directory/report_generator.py >> /home/pi/your-project-directory/report_cron.log 2>&1
```

**Important:** Replace `/home/pi/your-project-directory` with your actual project path!

## Understanding the Crontab Schedule

```
0 2 1 * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, where 0 and 7 are Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

Examples of different schedules:
```bash
# Every day at 2:00 AM
0 2 * * *

# Every Monday at 9:00 AM
0 9 * * 1

# First day of every month at 2:00 AM (our default)
0 2 1 * *

# Last day of every month at 11:59 PM
59 23 28-31 * * [ $(date -d tomorrow +\%d) -eq 1 ]
```

## Manual Report Generation

You can generate reports manually at any time:

```bash
# Generate report for the previous month (default)
python report_generator.py

# Generate report for a specific month
python report_generator.py --month 2025-10

# Use a different database file
python report_generator.py --db /path/to/inventory.db

# Combine options
python report_generator.py --month 2025-09 --db custom_inventory.db
```

## Database Schema

The SQLite database (`inventory.db`) contains a single table:

```sql
CREATE TABLE inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    item_name TEXT NOT NULL,
    item_count INTEGER NOT NULL
);
```

Indexes are created on `timestamp` and `item_name` for optimal query performance.

## Report Metrics Explained

The generated CSV report includes the following metrics for each item:

### 1. Total Consumed (Sales)
- **Definition:** Total number of units sold or consumed
- **Calculation:** Sum of all count decreases between consecutive logs
- **Example:** If count goes from 10 → 7 → 5, consumed = (10-7) + (7-5) = 5

### 2. Total Restocked
- **Definition:** Total number of units added to inventory
- **Calculation:** Sum of all count increases between consecutive logs
- **Example:** If count goes from 5 → 8 → 12, restocked = (8-5) + (12-8) = 7

### 3. Average Stock Level
- **Definition:** Average number of units in stock throughout the month
- **Calculation:** Mean of all recorded counts
- **Example:** Counts [10, 8, 6, 5, 10] → average = 7.8

### 4. End of Month Stock
- **Definition:** Final inventory count at month end
- **Calculation:** Last recorded count in the reporting period
- **Example:** Most recent database entry for that item

## Report File Format

Generated reports are named with the format:
```
inventory_report_YYYY-MONTH.csv
```

Example: `inventory_report_2025-october.csv`

CSV structure:
```csv
Item Name,Total Consumed (Sales),Total Restocked,Average Stock Level,End of Month Stock
Cantaloupe,45,50,8.5,12
Mango,38,40,6.2,8
Pineapple,52,55,9.1,10
...
```

## Monitoring and Troubleshooting

### Check Cron Job Status

View your scheduled cron jobs:
```bash
crontab -l
```

### View Logs

Check the cron execution log:
```bash
tail -f report_cron.log
```

Check the report generator's detailed log:
```bash
tail -f report_generator.log
```

Check general inventory events:
```bash
tail -f inventory_events.log
```

### Test Email Configuration

Test if email sending works:
```bash
python3 -c "from notify_enhanced import send_email; send_email('Test Subject', 'Test body message', None)"
```

### Common Issues

#### 1. No email received
- **Check credentials:** Verify SMTP_USER, SMTP_PASS are correct
- **Gmail users:** Make sure you're using an App Password, not your regular password
- **Check spam folder:** First emails might go to spam
- **View logs:** Check `report_generator.log` for error messages

#### 2. Database not found
- **Check path:** Ensure `inventory.db` exists in the script directory
- **Run main first:** The database is created when you first run `main_with_logging.py`
- **Permissions:** Make sure the script has write permissions in the directory

#### 3. No data in report
- **Check date range:** Make sure data exists for the queried month
- **Verify logging:** Confirm `main_with_logging.py` has been running
- **Query database:** Use SQLite to manually check data
  ```bash
  sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"
  ```

#### 4. Cron job not running
- **Check cron service:** `sudo service cron status`
- **Verify paths:** Use absolute paths in crontab, not relative
- **Check permissions:** Script must be executable
- **Environment variables:** Cron runs in limited environment; variables in crontab may not load from .bashrc

### Manually Query the Database

You can inspect the database using SQLite command line:

```bash
# Open database
sqlite3 inventory.db

# View table structure
.schema inventory_log

# Count total records
SELECT COUNT(*) FROM inventory_log;

# View recent entries
SELECT * FROM inventory_log ORDER BY timestamp DESC LIMIT 10;

# Check data for specific item
SELECT * FROM inventory_log WHERE item_name = 'Cantaloupe' ORDER BY timestamp DESC LIMIT 20;

# Exit SQLite
.quit
```

## File Structure

Your project directory should contain:

```
your-project-directory/
├── main_with_logging.py          # Enhanced main script with DB logging
├── report_generator.py            # Monthly report generator
├── notify_enhanced.py             # Enhanced notification module
├── notify.py                      # Original notification module (can keep both)
├── config.yaml                    # Configuration file
├── best.pt                        # YOLOv8 model
├── inventory.db                   # SQLite database (created automatically)
├── setup_automation.sh            # Automated setup script
├── AUTOMATION_GUIDE.md           # This file
├── report_cron.log               # Cron execution log
├── report_generator.log          # Report generator log
└── inventory_events.log          # Inventory events log
```

## Best Practices

1. **Backup Database:** Regularly backup `inventory.db`
   ```bash
   cp inventory.db inventory_backup_$(date +%Y%m%d).db
   ```

2. **Monitor Disk Space:** The database will grow over time
   ```bash
   du -h inventory.db
   ```

3. **Archive Old Reports:** Move old CSV reports to archive folder
   ```bash
   mkdir -p reports_archive
   mv inventory_report_*.csv reports_archive/
   ```

4. **Test Before Production:** Always test the full system before relying on it
   ```bash
   python report_generator.py --month $(date +%Y-%m)
   ```

5. **Set Up Notifications:** Consider adding a notification when reports are generated successfully

## Advanced Configuration

### Change Report Schedule

To change when reports are generated, modify the crontab:

```bash
# Run at midnight on the 1st
0 0 1 * * cd /path/to/project && python3 report_generator.py

# Run at 6:00 PM on the last day of each month
0 18 28-31 * * [ $(date -d tomorrow +\%d) -eq 1 ] && cd /path/to/project && python3 report_generator.py
```

### Generate Weekly Reports

Add an additional cron job for weekly reports:

```bash
# Every Monday at 8:00 AM
0 8 * * 1 cd /path/to/project && python3 report_generator.py --week
```

(Note: You would need to modify `report_generator.py` to support `--week` flag)

### Multiple Recipients

To send reports to multiple recipients, update the `NOTIFY_TO` variable:

```bash
export NOTIFY_TO="recipient1@example.com,recipient2@example.com"
```

## Support

For issues or questions:
1. Check the logs (`report_generator.log`, `report_cron.log`)
2. Verify email credentials
3. Test components individually
4. Review this guide's troubleshooting section

---

**System Version:** 1.0  
**Last Updated:** October 2025  
**Compatible with:** YOLOv8, Python 3.7+, Raspberry Pi OS

