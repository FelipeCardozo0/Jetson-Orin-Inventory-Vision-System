# 📚 Automated Monthly Reporting System - Documentation Index

This index helps you quickly find the right documentation for your needs.

---

## 🚀 Getting Started (Read These First)

| Document | Purpose | When to Read |
|----------|---------|-------------|
| **[REPORTING_SYSTEM_SUMMARY.md](REPORTING_SYSTEM_SUMMARY.md)** | Complete overview of what the system does | Start here! |
| **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** | Step-by-step setup checklist | During installation |
| **[CRON_SETUP.txt](CRON_SETUP.txt)** | Quick reference for cron configuration | When scheduling |

---

## 📖 Detailed Documentation

| Document | Purpose | When to Read |
|----------|---------|-------------|
| **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** | Comprehensive guide covering everything | For deep understanding |
| **[SYSTEM_ARCHITECTURE.txt](SYSTEM_ARCHITECTURE.txt)** | Visual architecture and data flow | To understand how it works |

---

## 💻 Code Files

### Core Scripts

| File | Purpose | Run When |
|------|---------|----------|
| **main_with_logging.py** | Enhanced main script with database logging | 24/7 (replaces main.py) |
| **report_generator.py** | Generates monthly reports and sends emails | Automatic (cron) or manual |
| **notify_enhanced.py** | Email module with CSV attachment support | Called by other scripts |

### Setup & Configuration

| File | Purpose | Run When |
|------|---------|----------|
| **setup_automation.sh** | Automated setup script | Once during installation |
| **requirements-reporting.txt** | Python dependencies | `pip install -r requirements-reporting.txt` |

---

## 📋 Quick Reference Guides

### For Installation
1. Read **REPORTING_SYSTEM_SUMMARY.md** (5 min)
2. Follow **SETUP_CHECKLIST.md** (15-30 min)
3. Use **setup_automation.sh** for automatic setup (recommended)
4. Or manually configure using **AUTOMATION_GUIDE.md**

### For Troubleshooting
1. Check **SETUP_CHECKLIST.md** troubleshooting section
2. Review **AUTOMATION_GUIDE.md** troubleshooting section
3. Read log files: `report_generator.log`, `report_cron.log`

### For Understanding the System
1. View **SYSTEM_ARCHITECTURE.txt** for visual overview
2. Read **REPORTING_SYSTEM_SUMMARY.md** for feature descriptions
3. Review code comments in Python files

### For Cron Configuration
1. Use **CRON_SETUP.txt** for quick reference
2. See **AUTOMATION_GUIDE.md** for detailed cron examples

---

## 🔍 Finding Specific Information

### "How do I set up email?"
- **Quick:** CRON_SETUP.txt → Environment Variables section
- **Detailed:** AUTOMATION_GUIDE.md → Step 2: Configure Email Settings

### "How do I schedule monthly reports?"
- **Quick:** CRON_SETUP.txt
- **Detailed:** AUTOMATION_GUIDE.md → Step 5: Set Up Cron Job

### "What metrics are calculated?"
- **Quick:** REPORTING_SYSTEM_SUMMARY.md → What's in the Report
- **Detailed:** AUTOMATION_GUIDE.md → Report Metrics Explained

### "How does the system work?"
- **Visual:** SYSTEM_ARCHITECTURE.txt
- **Written:** REPORTING_SYSTEM_SUMMARY.md → How It Works

### "Something isn't working!"
- **Quick check:** SETUP_CHECKLIST.md → Troubleshooting Checklist
- **Detailed help:** AUTOMATION_GUIDE.md → Monitoring and Troubleshooting

### "How do I manually generate a report?"
- **Command:**
  ```bash
  python3 report_generator.py
  ```
- **Options:** AUTOMATION_GUIDE.md → Manual Report Generation

### "What files are created?"
- **List:** REPORTING_SYSTEM_SUMMARY.md → Files Delivered
- **Structure:** AUTOMATION_GUIDE.md → File Structure

---

## 📊 File Types Explained

### Documentation Files (.md, .txt)

| Extension | Purpose | Open With |
|-----------|---------|-----------|
| `.md` | Markdown documentation | Any text editor, GitHub, VS Code |
| `.txt` | Plain text reference | Any text editor, terminal |

### Code Files (.py)

| File | Language | Purpose |
|------|----------|---------|
| `.py` | Python 3 | Executable scripts |

### Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `config.yaml` | System configuration | YAML |
| `~/.bashrc` | Environment variables | Bash script |
| `crontab` | Scheduled tasks | Cron syntax |

### Data Files (Created at Runtime)

| File | Purpose | Format |
|------|---------|--------|
| `inventory.db` | Historical data | SQLite database |
| `inventory_report_*.csv` | Monthly reports | CSV (Excel-compatible) |
| `*.log` | Error and event logs | Plain text |

---

## 🎯 Use Case Quick Links

### "I'm setting this up for the first time"
1. [REPORTING_SYSTEM_SUMMARY.md](REPORTING_SYSTEM_SUMMARY.md) - Overview
2. [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Follow step by step
3. Run `setup_automation.sh` - Automated setup

### "I want to understand how it works"
1. [SYSTEM_ARCHITECTURE.txt](SYSTEM_ARCHITECTURE.txt) - Visual diagrams
2. [REPORTING_SYSTEM_SUMMARY.md](REPORTING_SYSTEM_SUMMARY.md) - How It Works section
3. [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Deep dive

### "I need to troubleshoot an issue"
1. Check log files: `tail -f report_generator.log`
2. [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Troubleshooting section
3. [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Common Issues section

### "I want to modify the system"
1. Read code comments in `.py` files
2. [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Advanced Configuration
3. Modify and test scripts manually first

### "I need to set up cron"
1. [CRON_SETUP.txt](CRON_SETUP.txt) - Quick reference
2. Copy/paste the exact command for your system
3. Verify with `crontab -l`

---

## 📅 Recommended Reading Order

### For Beginners
1. **Day 1:** REPORTING_SYSTEM_SUMMARY.md (understand what you're building)
2. **Day 1:** SETUP_CHECKLIST.md (follow installation steps)
3. **Day 2:** CRON_SETUP.txt (schedule automatic reports)
4. **Week 1:** AUTOMATION_GUIDE.md (learn advanced features)

### For Experienced Users
1. REPORTING_SYSTEM_SUMMARY.md → Technical Details
2. SYSTEM_ARCHITECTURE.txt → Full architecture
3. Code files → Read source code
4. AUTOMATION_GUIDE.md → Advanced Configuration

---

## 🔗 External Resources

### Python Documentation
- [SQLite3 Module](https://docs.python.org/3/library/sqlite3.html)
- [CSV Module](https://docs.python.org/3/library/csv.html)
- [datetime Module](https://docs.python.org/3/library/datetime.html)

### System Administration
- [Crontab Guru](https://crontab.guru/) - Cron schedule expressions
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Systemd Services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

### YOLOv8
- [Ultralytics Documentation](https://docs.ultralytics.com/)

---

## 📞 Support Workflow

If you encounter issues, follow this workflow:

```
Issue Encountered
       ↓
Check SETUP_CHECKLIST.md → Troubleshooting
       ↓
Still not working?
       ↓
Check log files (*.log)
       ↓
Still not working?
       ↓
Read AUTOMATION_GUIDE.md → Monitoring and Troubleshooting
       ↓
Still not working?
       ↓
Test components individually:
  - Test email: python3 -c "from notify_enhanced import send_email; ..."
  - Test database: sqlite3 inventory.db .tables
  - Test report: python3 report_generator.py
       ↓
Identify failing component
       ↓
Review relevant documentation section
       ↓
Apply fix and retest
```

---

## 🎓 Learning Path

### Beginner Level
- [ ] Understand what the system does (REPORTING_SYSTEM_SUMMARY.md)
- [ ] Install and configure (SETUP_CHECKLIST.md)
- [ ] Run test report manually
- [ ] Schedule with cron (CRON_SETUP.txt)

### Intermediate Level
- [ ] Understand architecture (SYSTEM_ARCHITECTURE.txt)
- [ ] Read full guide (AUTOMATION_GUIDE.md)
- [ ] Query database manually
- [ ] Modify report metrics

### Advanced Level
- [ ] Modify Python scripts for custom features
- [ ] Set up systemd service
- [ ] Create database backups
- [ ] Build custom analytics on top of data

---

## 📦 Complete File List

### Must Have (Required)
- ✅ main_with_logging.py
- ✅ report_generator.py
- ✅ notify_enhanced.py (or updated notify.py)
- ✅ config.yaml
- ✅ best.pt

### Documentation (Helpful)
- 📖 REPORTING_SYSTEM_SUMMARY.md
- 📖 AUTOMATION_GUIDE.md
- 📖 SETUP_CHECKLIST.md
- 📖 SYSTEM_ARCHITECTURE.txt
- 📖 CRON_SETUP.txt
- 📖 INDEX.md (this file)

### Setup Files (Optional but recommended)
- 🔧 setup_automation.sh
- 🔧 requirements-reporting.txt

### Generated at Runtime
- 💾 inventory.db (database)
- 📊 inventory_report_*.csv (reports)
- 📝 *.log (logs)

---

## 🎯 Quick Commands

### Installation
```bash
pip install -r requirements-reporting.txt
./setup_automation.sh
```

### Run Main Script
```bash
python3 main_with_logging.py --headless &
```

### Generate Report
```bash
python3 report_generator.py
```

### Check Database
```bash
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"
```

### View Logs
```bash
tail -f report_generator.log
```

### Check Cron
```bash
crontab -l
```

---

## ✅ System Health Check

Run these commands to verify everything is working:

```bash
# 1. Check if main script is running
ps aux | grep main_with_logging.py

# 2. Check database exists and has data
sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"

# 3. Check cron job is scheduled
crontab -l | grep report_generator

# 4. Check recent logs for errors
tail -20 report_generator.log | grep -i error

# 5. Test email configuration
echo $SMTP_USER  # Should show your email

# 6. Check disk space
df -h .
du -h inventory.db
```

---

**Last Updated:** October 2025  
**System Version:** 1.0  
**For:** YOLOv8 Inventory Detection System

---

## 🌟 Quick Start for the Impatient

```bash
# 1. Setup (5 minutes)
chmod +x setup_automation.sh && ./setup_automation.sh

# 2. Start logging (1 minute)
python3 main_with_logging.py --headless &

# 3. Test report (2 minutes)
python3 report_generator.py --month $(date +%Y-%m)

# 4. Done! Check your email.
```

That's it! The system is now running autonomously.

---

**Need help? Start with REPORTING_SYSTEM_SUMMARY.md**

