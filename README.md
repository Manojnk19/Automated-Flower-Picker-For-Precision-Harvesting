# Rose Harvester FPV Controller

This project allows you to control a rose harvesting rover and its robotic arm via a modern FPV-style web interface. It includes live video feed with rose detection using YOLOv5, wheel and arm control, and network access for multiple users.

## Features
- Live video feed with YOLOv5-based rose detection and bounding boxes.
- Rover control (4 wheels, slow 50% speed) via web buttons.
- Robotic arm control:
  - Base (360° servo)
  - Shoulder (incremental 5° movement)
  - Elbow (incremental 5° movement)
  - Wrist (incremental 5° movement)
  - Gripper (open/close 0°/90°)
- Network-accessible web interface (any device on the same network can control).
- Safe cleanup of GPIO pins and video stream on exit.

## Project Structure
```
Rose-harvester-fpv-controller/
│
├─ app.py                  # Main Flask application
├─ rover_control.py        # Rover wheel control functions
├─ arm_control.py          # Robotic arm control functions
├─ rose_detector/
│  └─ detector.py          # YOLOv5 rose detection
├─ static/
│  ├─ index.html           # Web UI
│  ├─ style.css            # Web UI CSS
│  └─ script.js            # Web UI JS
└─ README.md
```

## Installation
1. Clone the repository:
```bash
git clone <repository_url>
cd Rose-harvester-fpv-controller
```
2. Create a Python virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python app.py
```
- Access the web UI at `http://<raspberry_pi_ip>:5000`
- Multiple users on the network can access and control simultaneously.

## Requirements
- Python 3.7+
- Raspberry Pi or similar with GPIO
- Servos and L298N motor driver connected as per pin configuration
- Packages:
```
Flask
opencv-python
torch
torchvision
RPi.GPIO
numpy
```

## Notes
- Ensure the YOLOv5 model path in `detector.py` is correct.
- Use `Ctrl+C` to stop the server safely; GPIO and camera will be released automatically.
- Web interface has transparent joystick/buttons for a modern FPV feel.

## License
MIT License