# 📊 YOLOv8 Automated Monthly Reporting System

> **Automatically track inventory, generate reports, and email monthly performance analytics**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What This Does

This system adds **automated monthly reporting** to your YOLOv8 inventory detection project. Once set up, it:

1. **📝 Logs** every inventory detection to a SQLite database (24/7)
2. **📊 Calculates** sales, restocking, and stock level metrics monthly
3. **📧 Emails** a comprehensive CSV report automatically on the 1st of each month
4. **🔄 Runs** completely hands-free - no manual intervention required

### Sample Report

```csv
Item Name,Total Consumed (Sales),Total Restocked,Average Stock Level,End of Month Stock
Cantaloupe,45,50,8.5,12
Mango,38,40,6.2,8
Pineapple,52,55,9.1,10
Sprite,67,70,11.3,15
```

---

## ⚡ Quick Start

### 1️⃣ Install Dependencies
```bash
pip install python-dateutil
```

### 2️⃣ Run Automated Setup
```bash
chmod +x setup_automation.sh
./setup_automation.sh
```

### 3️⃣ Start Enhanced Main Script
```bash
python3 main_with_logging.py --headless &
```

### 4️⃣ Done!
Reports will be automatically generated and emailed at **2:00 AM on the 1st of each month**.

---

## 📁 Files Included

### Core Scripts
- **main_with_logging.py** - Enhanced detection script with database logging
- **report_generator.py** - Monthly report generator with email delivery
- **notify_enhanced.py** - Email module supporting CSV attachments

### Documentation
- **INDEX.md** - Navigate all documentation ⭐ Start here
- **REPORTING_SYSTEM_SUMMARY.md** - Complete system overview
- **AUTOMATION_GUIDE.md** - Comprehensive setup and usage guide
- **SETUP_CHECKLIST.md** - Step-by-step installation checklist
- **SYSTEM_ARCHITECTURE.txt** - Visual architecture diagrams
- **CRON_SETUP.txt** - Quick cron job reference

### Setup Tools
- **setup_automation.sh** - Automated installation script
- **requirements-reporting.txt** - Python dependencies

---

## 🚀 Features

✅ **Continuous Data Logging**
- Every detection saved to SQLite database
- Timestamps, item names, and counts recorded
- Historical data for trend analysis

✅ **Comprehensive Metrics**
- Total consumed/sold per item
- Total restocked per item  
- Average stock levels
- End-of-month inventory

✅ **Automated Email Delivery**
- Professional CSV reports
- Scheduled monthly delivery
- Gmail/SMTP support

✅ **Zero Maintenance**
- Set it and forget it
- Automatic reconnection on failures
- Comprehensive error logging

✅ **Production Ready**
- Tested on Raspberry Pi
- Handles large datasets
- Optimized database queries

---

## 📊 Metrics Explained

### Total Consumed (Sales)
Sum of all inventory decreases. If stock goes from 10 → 8 → 5, consumed = 5 units.

### Total Restocked
Sum of all inventory increases. If stock goes from 5 → 10 → 15, restocked = 10 units.

### Average Stock Level
Mean inventory count throughout the month.

### End of Month Stock
Final inventory count on the last day of the month.

---

## 🔧 Configuration

### Email Settings (Gmail)

Add to `~/.bashrc`:
```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-app-password"
export NOTIFY_TO="recipient@example.com"
```

**Important:** Gmail requires an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### Cron Schedule

Edit with `crontab -e`:
```bash
# Run at 2:00 AM on the 1st of every month
0 2 1 * * cd /your/project/path && python3 report_generator.py >> report_cron.log 2>&1
```

---

## 🧪 Testing

### Test Manual Report Generation
```bash
python3 report_generator.py --month $(date +%Y-%m)
```

### Test Email Configuration
```bash
python3 -c "from notify_enhanced import send_email; send_email('Test', 'Body', None)"
```

### Verify Database Logging
```bash
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"
```

### Check Cron Job
```bash
crontab -l | grep report_generator
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[INDEX.md](INDEX.md)** | 📚 Master documentation index - start here! |
| **[REPORTING_SYSTEM_SUMMARY.md](REPORTING_SYSTEM_SUMMARY.md)** | 📋 Complete system overview |
| **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** | ✅ Installation checklist |
| **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** | 📖 Comprehensive guide |
| **[SYSTEM_ARCHITECTURE.txt](SYSTEM_ARCHITECTURE.txt)** | 🏗️ Visual diagrams |
| **[CRON_SETUP.txt](CRON_SETUP.txt)** | ⏰ Cron quick reference |

---

## 🐛 Troubleshooting

### No email received?
- Verify credentials: `echo $SMTP_USER`
- Check spam folder
- View logs: `cat report_generator.log`
- Use Gmail App Password, not regular password

### Database not found?
- Run `main_with_logging.py` first to create database
- Check file exists: `ls -l inventory.db`
- Verify permissions: `chmod 644 inventory.db`

### Cron job not running?
- Check service: `sudo service cron status`
- Use absolute paths in crontab
- View execution log: `cat report_cron.log`

See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for comprehensive troubleshooting.

---

## 📂 Database Schema

```sql
CREATE TABLE inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    item_name TEXT NOT NULL,
    item_count INTEGER NOT NULL
);
```

---

## 🔍 Manual Database Queries

```bash
# Open database
sqlite3 inventory.db

# Count total records
SELECT COUNT(*) FROM inventory_log;

# View recent entries
SELECT * FROM inventory_log ORDER BY timestamp DESC LIMIT 10;

# Get data for specific item
SELECT * FROM inventory_log WHERE item_name = 'Mango' 
ORDER BY timestamp DESC LIMIT 20;

# Exit
.quit
```

---

## 📊 Report File Naming

Reports are saved as:
```
inventory_report_YYYY-MONTH.csv
```

Examples:
- `inventory_report_2025-october.csv`
- `inventory_report_2025-november.csv`
- `inventory_report_2025-december.csv`

---

## 🔄 System Workflow

```
1. main_with_logging.py (24/7)
   ↓ Logs detections
   
2. inventory.db (SQLite)
   ↓ Stores historical data
   
3. report_generator.py (Monthly @ 2 AM)
   ↓ Analyzes data & generates CSV
   
4. notify_enhanced.py
   ↓ Sends email with attachment
   
5. Your Email Inbox 📧
   ✓ Monthly report received!
```

---

## 💡 Tips & Best Practices

### Backup Your Database
```bash
cp inventory.db inventory_backup_$(date +%Y%m%d).db
```

### Monitor Disk Space
```bash
du -h inventory.db
```

### View Real-Time Logs
```bash
tail -f inventory_events.log
```

### Archive Old Reports
```bash
mkdir -p reports_archive
mv inventory_report_*.csv reports_archive/
```

---

## 🎓 Learning Resources

### Beginner Path
1. Read [REPORTING_SYSTEM_SUMMARY.md](REPORTING_SYSTEM_SUMMARY.md)
2. Follow [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
3. Run `setup_automation.sh`
4. Wait for first report

### Advanced Path
1. Study [SYSTEM_ARCHITECTURE.txt](SYSTEM_ARCHITECTURE.txt)
2. Read [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
3. Modify Python scripts for custom features
4. Build analytics dashboards

---

## 📋 System Requirements

- **Hardware:** Raspberry Pi 3B+ or better
- **OS:** Raspberry Pi OS / Linux
- **Python:** 3.7 or higher
- **Storage:** ~50 MB/month for database
- **RAM:** ~100 MB additional
- **Network:** Internet access for email

---

## 🎉 Success Indicators

Your system is working correctly when:

✅ `inventory.db` grows steadily  
✅ Monthly reports appear in your email  
✅ CSV files contain accurate metrics  
✅ No errors in log files  
✅ Cron job runs automatically  

---

## 📞 Support

**Need help?**
1. Check [INDEX.md](INDEX.md) to find the right documentation
2. Review [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) troubleshooting section
3. Read [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for detailed help
4. Check log files for specific errors

---

## 🔐 Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive data
- Use Gmail App Passwords (not regular passwords)
- Restrict database file permissions: `chmod 600 inventory.db`
- Backup database regularly

---

## 🚀 Advanced Usage

### Generate Report for Specific Month
```bash
python3 report_generator.py --month 2025-10
```

### Use Custom Database
```bash
python3 main_with_logging.py --db /path/to/custom.db
python3 report_generator.py --db /path/to/custom.db
```

### Run in Headless Mode
```bash
python3 main_with_logging.py --headless
```

---

## 📈 Future Enhancements

Potential additions (not included, but possible):
- Web dashboard for real-time monitoring
- Weekly/daily reports
- Predictive analytics
- Mobile app notifications
- Multi-store support
- Integration with POS systems

---

## 🏆 Benefits

### For Business Owners
- 📊 Data-driven inventory decisions
- 💰 Reduce waste from overstocking
- 📉 Avoid lost sales from stockouts
- 📧 Automatic reporting saves time
- 📈 Track trends over time

### For Developers
- 🐍 Clean, well-documented Python code
- 🗄️ Efficient SQLite database design
- 📦 Modular, maintainable architecture
- 🧪 Easy to test and debug
- 🔧 Simple to extend and customize

---

## 📜 License

MIT License - Free to use and modify for your inventory system.

---

## 🙏 Acknowledgments

Built for the YOLOv8 inventory detection system using:
- **Ultralytics YOLOv8** - Object detection
- **SQLite** - Data storage
- **Python** - Core language
- **FastAPI** - (For web monitoring system)

---

## 📅 Version History

- **v1.0** (October 2025) - Initial release
  - Database logging
  - Monthly report generation
  - Email delivery
  - Automated scheduling

---

## ✅ Quick Health Check

Run this to verify everything is working:

```bash
# Check main script is running
ps aux | grep main_with_logging

# Check database has data
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"

# Check cron job scheduled
crontab -l | grep report_generator

# Check for errors
tail -20 report_generator.log | grep -i error
```

---

## 🎯 Next Steps

1. ✅ Install the system ([SETUP_CHECKLIST.md](SETUP_CHECKLIST.md))
2. ✅ Test report generation
3. ✅ Schedule with cron
4. ✅ Wait for first automated report
5. ✅ Analyze your inventory data!

---

**Ready to get started? → [INDEX.md](INDEX.md)**

---

*Built with ❤️ for automated inventory management*

