# 📋 Automated Reporting System - Setup Checklist

Use this checklist to ensure your automated monthly reporting system is properly configured.

---

## ✅ Pre-Installation

- [ ] Raspberry Pi is running and accessible
- [ ] Python 3.7+ is installed (`python3 --version`)
- [ ] Existing YOLOv8 system is working
- [ ] You have access to `best.pt` model file
- [ ] You have email credentials ready (Gmail App Password recommended)

---

## ✅ Installation Steps

### Step 1: Install Dependencies

- [ ] Run: `pip install python-dateutil`
- [ ] Verify: `python3 -c "import dateutil; print('OK')"`

### Step 2: Configure Email

**Option A: Using setup script (Recommended)**
- [ ] Run: `chmod +x setup_automation.sh`
- [ ] Run: `./setup_automation.sh`
- [ ] Follow prompts to enter email credentials

**Option B: Manual configuration**
- [ ] Edit `~/.bashrc`
- [ ] Add email environment variables:
  ```bash
  export SMTP_HOST="smtp.gmail.com"
  export SMTP_PORT="465"
  export SMTP_USER="your-email@gmail.com"
  export SMTP_PASS="your-app-password"
  export NOTIFY_FROM="your-email@gmail.com"
  export NOTIFY_TO="recipient@example.com"
  ```
- [ ] Run: `source ~/.bashrc`
- [ ] Verify: `echo $SMTP_USER` (should show your email)

### Step 3: Update Notification Module

**Choose ONE option:**

**Option A: Replace existing notify.py**
- [ ] Backup original: `cp notify.py notify_original.py`
- [ ] Replace: `cp notify_enhanced.py notify.py`

**Option B: Keep both files**
- [ ] Keep `notify.py` as-is
- [ ] Keep `notify_enhanced.py` (already imported in report_generator.py)

### Step 4: Start Enhanced Main Script

- [ ] Test run: `python3 main_with_logging.py`
- [ ] Verify camera opens (if not headless)
- [ ] Check for errors in terminal
- [ ] Verify `inventory.db` is created: `ls -lh inventory.db`
- [ ] For production: `python3 main_with_logging.py --headless &`

### Step 5: Verify Database Logging

- [ ] Let script run for 1-2 minutes
- [ ] Check database: `sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"`
- [ ] Should show multiple records (one per item per detection cycle)
- [ ] View sample: `sqlite3 inventory.db "SELECT * FROM inventory_log LIMIT 10;"`

### Step 6: Configure Cron Job

**If you used setup script:**
- [ ] Verify: `crontab -l | grep report_generator`
- [ ] Should see scheduled job

**If manual setup:**
- [ ] Open crontab: `crontab -e`
- [ ] Add line (replace `/path/to/project`):
  ```
  0 2 1 * * cd /path/to/project && /usr/bin/python3 /path/to/project/report_generator.py >> /path/to/project/report_cron.log 2>&1
  ```
- [ ] Save and exit
- [ ] Verify: `crontab -l`

---

## ✅ Testing

### Test 1: Database Verification

- [ ] Run: `sqlite3 inventory.db`
- [ ] Run: `.tables` (should show `inventory_log`)
- [ ] Run: `.schema inventory_log` (verify table structure)
- [ ] Run: `SELECT COUNT(*) FROM inventory_log;` (should be > 0)
- [ ] Run: `.quit`

### Test 2: Manual Report Generation

- [ ] Run: `python3 report_generator.py --month $(date +%Y-%m)`
- [ ] Check for CSV file: `ls -l inventory_report_*.csv`
- [ ] Open CSV and verify data looks correct
- [ ] Check logs: `cat report_generator.log`

### Test 3: Email Delivery

- [ ] Check your email inbox
- [ ] Should have received "Monthly Inventory Performance Report"
- [ ] Email should have CSV attachment
- [ ] Open CSV in Excel/Google Sheets to verify format

### Test 4: Email Configuration Test

- [ ] Run: `python3 -c "from notify_enhanced import send_email; result = send_email('Test Subject', 'Test body', None); print('Success!' if result else 'Failed')"`
- [ ] Check email inbox for test message

### Test 5: Cron Job Verification

- [ ] Run: `crontab -l`
- [ ] Verify cron job is listed
- [ ] Run: `sudo service cron status`
- [ ] Should show "active (running)"

---

## ✅ Production Readiness

### File Permissions

- [ ] Database writable: `ls -l inventory.db`
- [ ] Log files writable: `ls -l *.log`
- [ ] Scripts readable: `ls -l *.py`

### Background Execution

**For 24/7 operation, consider using systemd service:**

- [ ] Create service file: `/etc/systemd/system/inventory-logger.service`
- [ ] Add configuration (see AUTOMATION_GUIDE.md)
- [ ] Enable service: `sudo systemctl enable inventory-logger.service`
- [ ] Start service: `sudo systemctl start inventory-logger.service`
- [ ] Check status: `sudo systemctl status inventory-logger.service`

**Or use screen/tmux:**

- [ ] Install screen: `sudo apt-get install screen`
- [ ] Start session: `screen -S inventory`
- [ ] Run script: `python3 main_with_logging.py --headless`
- [ ] Detach: Press `Ctrl+A` then `D`
- [ ] Reattach later: `screen -r inventory`

### Monitoring Setup

- [ ] Set calendar reminder to check logs weekly
- [ ] Create backup script for `inventory.db`
- [ ] Document your specific configuration
- [ ] Save email credentials securely

---

## ✅ Post-Installation

### Week 1

- [ ] Day 1: Verify logging is working
- [ ] Day 3: Check database size: `du -h inventory.db`
- [ ] Day 7: Review logs for any errors

### Month 1

- [ ] Wait for 1st of next month (or run test report)
- [ ] Check email for monthly report
- [ ] Review report for accuracy
- [ ] Verify cron executed: `cat report_cron.log`

### Ongoing

- [ ] Monthly: Review generated reports
- [ ] Monthly: Check disk space
- [ ] Quarterly: Backup database
- [ ] Annually: Update dependencies

---

## 🐛 Troubleshooting Checklist

If something isn't working, check these:

### No Email Received

- [ ] SMTP credentials are correct: `echo $SMTP_USER $SMTP_PASS`
- [ ] Using Gmail App Password (not regular password)
- [ ] Check spam/junk folder
- [ ] Check report_generator.log: `tail -20 report_generator.log`
- [ ] Test email manually (Test 4 above)

### Database Errors

- [ ] Database file exists: `ls -l inventory.db`
- [ ] Database is writable: `chmod 644 inventory.db`
- [ ] Not a permission issue: `sudo -u $USER sqlite3 inventory.db .tables`

### Cron Job Not Running

- [ ] Cron service is running: `sudo service cron status`
- [ ] Cron job syntax is correct: `crontab -l`
- [ ] Using absolute paths (not relative)
- [ ] Check cron log: `tail -f report_cron.log`

### Empty Reports

- [ ] Database has data: `sqlite3 inventory.db "SELECT COUNT(*) FROM inventory_log;"`
- [ ] main_with_logging.py has been running long enough
- [ ] Querying correct month: `python3 report_generator.py --month YYYY-MM`

---

## 📊 Success Criteria

Your system is successfully set up when:

✅ **Database logging is continuous**
- Records are being added every few seconds
- Database size is growing steadily

✅ **Manual reports work**
- CSV files are generated
- Metrics look accurate
- Emails are delivered

✅ **Cron job is scheduled**
- Listed in `crontab -l`
- Will run automatically on the 1st of each month

✅ **All logs are clean**
- No errors in inventory_events.log
- No errors in report_generator.log
- No errors in report_cron.log

✅ **Documentation is understood**
- You know how to read logs
- You know how to manually generate reports
- You know how to troubleshoot issues

---

## 📁 Final File Check

Verify all these files exist in your project directory:

- [ ] `main_with_logging.py`
- [ ] `report_generator.py`
- [ ] `notify_enhanced.py` or updated `notify.py`
- [ ] `config.yaml`
- [ ] `best.pt`
- [ ] `inventory.db` (created after first run)
- [ ] `setup_automation.sh`
- [ ] `requirements-reporting.txt`
- [ ] `AUTOMATION_GUIDE.md`
- [ ] `REPORTING_SYSTEM_SUMMARY.md`
- [ ] `SYSTEM_ARCHITECTURE.txt`
- [ ] `CRON_SETUP.txt`
- [ ] `SETUP_CHECKLIST.md` (this file)

---

## 🎉 Completion

When all items are checked:

- [ ] **System is fully operational**
- [ ] **Documentation is reviewed**
- [ ] **Testing is complete**
- [ ] **Ready for production use**

**Congratulations!** Your automated inventory reporting system is now running!

The system will:
- ✅ Log all inventory detections 24/7
- ✅ Calculate comprehensive metrics
- ✅ Generate monthly CSV reports
- ✅ Email reports automatically
- ✅ Require no manual intervention

---

## 📞 Need Help?

1. **Review logs:** Most issues show up in log files
2. **Check documentation:** See AUTOMATION_GUIDE.md for detailed info
3. **Test components:** Run each script manually to isolate issues
4. **Verify configuration:** Double-check email settings and file paths

---

**Last Updated:** October 2025  
**Version:** 1.0

