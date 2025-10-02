# 🍲 Poke Bowl Inventory Management System

**AI-Powered Real-Time Inventory Tracking & Automated Reporting**

This project uses YOLOv8 computer vision to automatically detect and track poke bowl ingredients, providing real-time monitoring via web interface and automated monthly performance reports.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)

---

## 🎯 Features

### 🎥 Live Web Monitoring
- **Real-time video feeds** from 4 Raspberry Pi cameras
- **2x2 grid display** with live YOLOv8 detections
- **WebSocket streaming** for low latency
- **Auto-reconnection** on network failures

### 📊 Automated Monthly Reports
- **Continuous data logging** to SQLite database
- **Sales tracking** (items consumed)
- **Restock monitoring** (items added)
- **Performance metrics** (averages, trends)
- **Automatic email delivery** on 1st of each month

### 🔔 Smart Notifications
- **Low stock alerts** via email
- **Restock confirmations**
- **State change detection** (prevents spam)

---

## 📦 Project Structure

```
├── Web Monitoring System
│   ├── client.py                    # Raspberry Pi camera client
│   ├── server.py                    # Central FastAPI server
│   ├── index.html                   # Web interface (2x2 grid)
│   ├── requirements-client.txt      # Pi dependencies
│   └── requirements-server.txt      # Server dependencies
│
├── Automated Reporting System
│   ├── main_with_logging.py        # Enhanced main with DB logging
│   ├── report_generator.py         # Monthly report generator
│   ├── notify_enhanced.py          # Email with CSV attachments
│   ├── requirements-reporting.txt  # Reporting dependencies
│   └── setup_automation.sh         # Auto-setup script
│
├── Original Detection System
│   └── project-2-at-2025-09-11-20-06-14f25e97/
│       ├── main.py                 # Original detection script
│       ├── notify.py               # Original notifications
│       ├── config.yaml             # Configuration file
│       └── classes.txt             # YOLOv8 class names
│
├── Training Data
│   └── Images/                     # Training images by category
│       ├── Cantaloupe/
│       ├── Mango/
│       ├── Pineapple/
│       └── ...
│
├── Documentation
│   ├── INDEX.md                    # Documentation index
│   ├── REPORTING_README.md         # Reporting system guide
│   ├── AUTOMATION_GUIDE.md         # Complete automation guide
│   ├── SETUP_CHECKLIST.md          # Setup checklist
│   ├── SYSTEM_ARCHITECTURE.txt     # Architecture diagrams
│   └── CRON_SETUP.txt             # Cron job reference
│
└── Model
    └── best.pt                     # Trained YOLOv8 model
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Raspberry Pi(s) with camera
- Gmail account (for email reports)

### 1. Web Monitoring System

**On Server:**
```bash
pip install -r requirements-server.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

**On Each Raspberry Pi:**
```bash
pip install -r requirements-client.txt
python client.py ws://SERVER_IP:8000 cam1
```

**View in Browser:**
```
http://SERVER_IP:8000
```

### 2. Automated Reporting System

**Install & Configure:**
```bash
pip install -r requirements-reporting.txt
chmod +x setup_automation.sh
./setup_automation.sh
```

**Start Logging:**
```bash
python3 main_with_logging.py --headless &
```

**Done!** Reports will be emailed monthly automatically.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[INDEX.md](INDEX.md)** | Master documentation index |
| **[REPORTING_README.md](REPORTING_README.md)** | Reporting system overview |
| **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** | Complete setup guide |
| **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** | Step-by-step checklist |
| **[README.md](README.md)** | Web monitoring details |
| **[QUICKSTART.md](QUICKSTART.md)** | 3-step quick start |

---

## 🎓 How It Works

### Web Monitoring Flow
```
Raspberry Pi → YOLOv8 Detection → JPEG Encoding → WebSocket 
    ↓
Central Server ← WebSocket Connection ← Web Browser
    ↓
Broadcast to All Viewers → Real-time Display (2x2 Grid)
```

### Automated Reporting Flow
```
Camera → YOLOv8 → Item Counts → SQLite Database (24/7)
    ↓
Monthly: Analyze Data → Calculate Metrics → Generate CSV
    ↓
Email Report to Owner → Business Intelligence
```

---

## 📊 Sample Report Output

```csv
Item Name,Total Consumed (Sales),Total Restocked,Average Stock Level,End of Month Stock
Cantaloupe,45,50,8.5,12
Mango,38,40,6.2,8
Pineapple,52,55,9.1,10
Kilauea Lemon Cake,67,70,11.3,15
```

---

## 🔧 Configuration

### Email Setup (for Reports)
```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="465"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASS="your-gmail-app-password"
export NOTIFY_TO="recipient@example.com"
```

### Tracked Items
See `config.yaml` for the complete list of tracked poke bowl ingredients and beverages.

---

## 🧪 Testing

```bash
# Test web monitoring (local)
uvicorn server:app --host 0.0.0.0 --port 8000
python client.py ws://localhost:8000 cam1

# Test reporting system
python3 report_generator.py --month $(date +%Y-%m)

# Test email
python3 -c "from notify_enhanced import send_email; send_email('Test', 'Body', None)"
```

---

## 🛠️ Technology Stack

- **Computer Vision:** YOLOv8 (Ultralytics)
- **Backend:** FastAPI, WebSockets
- **Frontend:** HTML5, JavaScript (Vanilla)
- **Database:** SQLite
- **Email:** SMTP (Gmail)
- **Scheduling:** Cron
- **Hardware:** Raspberry Pi, Arducam

---

## 📈 Project Evolution

1. **Phase 1:** Basic YOLOv8 detection with email alerts
2. **Phase 2:** Added web-based live monitoring system
3. **Phase 3:** Implemented automated monthly reporting
4. **Current:** Production-ready inventory management solution

---

## 🎯 Use Cases

- **Restaurant Inventory:** Track ingredients in real-time
- **Retail Monitoring:** Monitor product stock levels
- **Supply Chain:** Automate reorder triggers
- **Analytics:** Data-driven inventory decisions

---

## 📝 License

MIT License - Free to use and modify

---

## 🙏 Acknowledgments

- **YOLOv8** by Ultralytics for object detection
- **FastAPI** for high-performance web framework
- **OpenCV** for computer vision operations

---

## 📞 Support

For detailed setup instructions, troubleshooting, and advanced configuration, see the complete documentation in the repository.

**Start here:** [INDEX.md](INDEX.md)

---

## 🌟 Star This Repo!

If you find this project useful, please give it a ⭐ on GitHub!

---

**Built for automated poke bowl inventory management** 🍲

