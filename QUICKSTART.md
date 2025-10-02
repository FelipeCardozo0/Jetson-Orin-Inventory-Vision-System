# Quick Start Guide

Get your YOLOv8 monitoring system running in 3 steps!

## Step 1: Start the Server

On your main computer (the server):

```bash
# Install dependencies
pip install -r requirements-server.txt

# Start the server
uvicorn server:app --host 0.0.0.0 --port 8000
```

**Note your server's IP address!** (e.g., 192.168.1.100)

## Step 2: Open the Web Interface

On any computer/tablet/phone on the same network, open a browser:

```
http://[YOUR_SERVER_IP]:8000
```

Example: `http://192.168.1.100:8000`

You should see the monitoring page with 4 empty camera slots.

## Step 3: Start the Raspberry Pi Clients

On each Raspberry Pi:

```bash
# Install dependencies (first time only)
pip install -r requirements-client.txt

# Copy your best.pt model to the same directory as client.py

# Start the client (replace IP and camera ID)
python client.py ws://192.168.1.100:8000 cam1
```

**Important:** Use a different camera ID for each Pi:
- Raspberry Pi 1: `cam1`
- Raspberry Pi 2: `cam2`
- Raspberry Pi 3: `cam3`
- Raspberry Pi 4: `cam4`

## That's It!

The web interface should now show live video feeds with YOLOv8 detections!

## Troubleshooting

### "Cannot connect to server"
- Make sure the server is running
- Check that you're using the correct IP address
- Verify both devices are on the same network
- Check firewall settings

### "Camera not found"
- Test camera: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`
- Try different camera index: `python client.py ws://... cam1 --camera 1`

### "No video showing"
- Check the browser console (F12) for errors
- Verify the client.py script is running without errors
- Check that `best.pt` model file exists

## Testing Without Raspberry Pi

You can test the system on your local machine first:

```bash
# Terminal 1: Start server
uvicorn server:app --host 0.0.0.0 --port 8000

# Terminal 2: Start a test client
python client.py ws://localhost:8000 cam1

# Browser: Open http://localhost:8000
```

This will use your computer's webcam for testing!

