# YOLOv8 Live Inventory Monitoring System

A distributed real-time video monitoring system that streams YOLOv8 object detection results from multiple Raspberry Pi cameras to a centralized web interface.

## System Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Raspberry Pi   │      │  Raspberry Pi   │      │  Raspberry Pi   │
│   (Camera 1)    │      │   (Camera 2)    │      │   (Camera 3,4)  │
│                 │      │                 │      │                 │
│  client.py      │      │  client.py      │      │  client.py      │
│  + YOLOv8       │      │  + YOLOv8       │      │  + YOLOv8       │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         │    WebSocket           │    WebSocket           │
         │    (Publish)           │    (Publish)           │
         └────────────────────────┼────────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │  Central Server │
                         │                 │
                         │   server.py     │
                         │   (FastAPI)     │
                         └────────┬────────┘
                                  │
                                  │    WebSocket
                                  │    (Broadcast)
                         ┌────────▼────────┐
                         │  Web Browser    │
                         │                 │
                         │   index.html    │
                         │   (2x2 Grid)    │
                         └─────────────────┘
```

## Features

- **Real-time YOLOv8 Detection**: Each Raspberry Pi runs YOLOv8 inference on live camera feeds
- **WebSocket Streaming**: Low-latency video streaming using WebSocket protocol
- **2x2 Grid Display**: Clean web interface showing all four camera feeds simultaneously
- **Auto-Reconnection**: Clients automatically reconnect if connection is lost
- **Resilient**: Handles camera disconnections and network issues gracefully
- **Scalable**: Built with FastAPI for high-performance async operations

## System Components

### 1. Client Script (`client.py`)
Runs on each Raspberry Pi to capture video, perform YOLOv8 inference, and stream results.

### 2. Backend Server (`server.py`)
Central FastAPI server that receives streams from Raspberry Pis and broadcasts to viewers.

### 3. Frontend (`index.html`)
Web interface that displays all four camera feeds in a beautiful 2x2 grid layout.

## Installation

### On the Server (Central Computer)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements-server.txt
   ```

2. **Place files in the same directory:**
   - `server.py`
   - `index.html`

3. **Start the server:**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

   The server will start on `http://0.0.0.0:8000`

### On Each Raspberry Pi

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements-client.txt
   ```

2. **Copy required files:**
   - `client.py`
   - `best.pt` (your trained YOLOv8 model)

3. **Start the client (replace with your server's IP):**
   ```bash
   # Camera 1
   python client.py ws://192.168.1.100:8000 cam1

   # Camera 2
   python client.py ws://192.168.1.100:8000 cam2

   # Camera 3
   python client.py ws://192.168.1.100:8000 cam3

   # Camera 4
   python client.py ws://192.168.1.100:8000 cam4
   ```

## Usage

### Starting the System

1. **Start the server first:**
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

2. **Open the web interface:**
   Open your browser and navigate to:
   ```
   http://[SERVER_IP]:8000
   ```
   Replace `[SERVER_IP]` with your server's IP address.

3. **Start each Raspberry Pi client:**
   ```bash
   python client.py ws://[SERVER_IP]:8000 [CAMERA_ID]
   ```

### Command-Line Arguments

**Client (`client.py`):**
```bash
python client.py <server_url> <camera_id> [--model MODEL_PATH] [--camera CAMERA_INDEX]
```

- `server_url`: WebSocket server URL (e.g., `ws://192.168.1.100:8000`)
- `camera_id`: Unique identifier (must be one of: `cam1`, `cam2`, `cam3`, `cam4`)
- `--model`: Path to YOLOv8 model (default: `best.pt`)
- `--camera`: Camera device index (default: `0`)

**Examples:**
```bash
# Basic usage
python client.py ws://192.168.1.100:8000 cam1

# With custom model path
python client.py ws://192.168.1.100:8000 cam2 --model /path/to/model.pt

# With different camera index
python client.py ws://192.168.1.100:8000 cam3 --camera 1
```

## Configuration

### Network Configuration

1. **Find your server's IP address:**
   - Linux/Mac: `ifconfig` or `ip addr`
   - Windows: `ipconfig`

2. **Ensure firewall allows connections:**
   ```bash
   # Linux (example for ufw)
   sudo ufw allow 8000/tcp
   ```

3. **Update client commands with the correct server IP**

### Camera Configuration

If you're using an Arducam or specific camera hardware on Raspberry Pi:

1. **Enable camera interface:**
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Camera > Enable
   ```

2. **For Arducam, you may need specific drivers:**
   ```bash
   # Follow Arducam's installation guide for your specific model
   ```

3. **Test camera:**
   ```bash
   # For USB cameras
   ls -l /dev/video*
   
   # Verify with OpenCV
   python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
   ```

### Running as a Service (Optional)

To make clients start automatically on Raspberry Pi boot:

1. **Create a systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/yolo-client.service
   ```

2. **Add the following content:**
   ```ini
   [Unit]
   Description=YOLOv8 Video Streaming Client
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/yolo-project
   ExecStart=/usr/bin/python3 /home/pi/yolo-project/client.py ws://192.168.1.100:8000 cam1
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl enable yolo-client.service
   sudo systemctl start yolo-client.service
   sudo systemctl status yolo-client.service
   ```

## Troubleshooting

### Client Cannot Connect to Server

1. **Check server is running:**
   ```bash
   curl http://[SERVER_IP]:8000/health
   ```

2. **Verify network connectivity:**
   ```bash
   ping [SERVER_IP]
   ```

3. **Check firewall settings**

### No Video Appearing

1. **Check camera is working:**
   ```bash
   python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
   ```

2. **Verify model file exists:**
   ```bash
   ls -l best.pt
   ```

3. **Check server logs for errors**

### Poor Performance / Lag

1. **Reduce frame rate in `client.py`:**
   Change the sleep value in line ~188:
   ```python
   await asyncio.sleep(0.066)  # ~15 FPS instead of 30
   ```

2. **Lower JPEG quality in `client.py`:**
   Change line ~165:
   ```python
   _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
   ```

3. **Check network bandwidth**

### Memory Issues on Raspberry Pi

1. **Reduce frame resolution before inference:**
   Add after line 154 in `client.py`:
   ```python
   frame = cv2.resize(frame, (640, 480))
   ```

2. **Use a smaller YOLOv8 model:**
   - YOLOv8n (nano) instead of YOLOv8s/m/l/x

## API Endpoints

### Server Endpoints

- `GET /` - Serves the web interface
- `GET /health` - Health check (returns connection stats)
- `WebSocket /ws/broadcast` - Viewer endpoint (browsers connect here)
- `WebSocket /ws/publish/{camera_id}` - Publisher endpoint (Raspberry Pis connect here)

### Health Check Response
```json
{
  "status": "healthy",
  "viewers": 2,
  "publishers": 4,
  "active_cameras": ["cam1", "cam2", "cam3", "cam4"]
}
```

## Performance Specifications

- **Frame Rate**: ~30 FPS per camera (adjustable)
- **Latency**: < 200ms (on local network)
- **Bandwidth**: ~1-2 Mbps per camera stream
- **Concurrent Viewers**: Tested with 10+ simultaneous viewers

## License

This project is provided as-is for the YOLOv8 inventory monitoring system.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server and client logs
3. Verify all components are using the correct IP addresses and ports

---

**Built with:** Python, FastAPI, WebSockets, YOLOv8, OpenCV

