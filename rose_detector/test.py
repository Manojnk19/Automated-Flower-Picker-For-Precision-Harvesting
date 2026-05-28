from flask import Flask, Response
import cv2
from detector import RoseDetector

# Initialize Flask app and RoseDetector
app = Flask(__name__)
detector = RoseDetector()

# Open video capture device (USB camera, change to your camera device if needed)
cap = cv2.VideoCapture('/dev/video0')  # Use '/dev/video1' or other device path if necessary

if not cap.isOpened():
    print("Error: Cannot open camera /dev/video0")
    exit()

def gen_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue  # Skip invalid frames
        
        # Process the frame with the RoseDetector to detect roses
        annotated_frame = detector.detect(frame)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame as part of the MJPEG stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video')
def video_feed():
    # This route returns the MJPEG stream of processed frames
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Main route returns a simple HTML page with the video stream
    return "<h1>Rose Detector Stream</h1><img src='/video'>"

if __name__ == '__main__':
    # Run Flask app on all available network interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)
