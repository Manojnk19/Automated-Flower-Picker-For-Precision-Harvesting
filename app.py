import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from flask import Flask, Response, jsonify, request, send_from_directory
import threading
import time
import atexit
from rover_control import RoverControl
from arm_control import ArmControl

# ---------------- FLASK APP ----------------
app = Flask(__name__, static_folder='static', static_url_path='/static')
rover = RoverControl()
arm = ArmControl()

# Align wrist at start
arm.wrist_angle = 90
arm._move_servo(arm.wrist_pin, arm.wrist_angle, 0.5)

automatic_mode = False
auto_stop_flag = threading.Event()

# ---------------- ROSE DETECTOR ----------------
class RoseDetector:
    def __init__(self, model_path='rose_detector/model/best.tflite', focal_length=615, real_width=6):
        self.interpreter = tflite.Interpreter(model_path=model_path, num_threads=4)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.focal_length = focal_length
        self.real_width = real_width
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def detect(self, frame):
        input_shape = self.input_details[0]['shape']
        img = cv2.resize(frame, (input_shape[2], input_shape[1])).astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        output_data = np.array(self.interpreter.get_tensor(self.output_details[0]['index']), copy=True)

        detections = []
        for det in output_data[0]:
            if len(det) < 6:
                continue
            x, y, w, h, conf, cls = det
            if conf > 0.4:
                h_frame, w_frame = frame.shape[:2]
                x1 = int((x - w / 2) * w_frame)
                y1 = int((y - h / 2) * h_frame)
                x2 = int((x + w / 2) * w_frame)
                y2 = int((y + h / 2) * h_frame)
                width_px = x2 - x1
                dist = (self.real_width * self.focal_length) / max(width_px,1)
                detections.append((x1, y1, x2, y2, conf, dist))

        # Remove overlapping boxes
        final = []
        detections = sorted(detections, key=lambda x: x[4], reverse=True)
        for det in detections:
            keep = True
            for f in final:
                iou = self._iou(det[:4], f[:4])
                if iou > 0.4:
                    keep = False
                    break
            if keep:
                final.append(det)
        return final

    def _iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2]-boxA[0])*(boxA[3]-boxA[1])
        boxBArea = (boxB[2]-boxB[0])*(boxB[3]-boxB[1])
        return interArea / float(boxAArea + boxBArea - interArea + 1e-5)

    def generate_frames(self):
        prev_time = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            current_time = time.time()
            if current_time - prev_time < 0.05:  # limit ~20 FPS
                time.sleep(0.01)
                continue
            prev_time = current_time

            detections = self.detect(frame)

            # Automatic arm control
            if automatic_mode:
                for x1, y1, x2, y2, conf, dist in detections:
                    center_x = (x1+x2)//2
                    frame_center = frame.shape[1]//2
                    offset = center_x - frame_center

                    if 15 < dist <= 20:
                        if offset > 50:
                            arm.move_base_right()
                        elif offset < -50:
                            arm.move_base_left()
                        else:
                            arm.shoulder_right()
                    elif dist <= 13:
                        arm.gripper_close()
                        cv2.putText(frame, "CUTTING", (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            # Draw boxes & distance
            for x1, y1, x2, y2, conf, dist in detections:
                cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame, f"{dist:.1f}cm", (x1, max(y1-10,20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0),2)

            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY),70])
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+buffer.tobytes()+b'\r\n')

    def release(self):
        if self.cap.isOpened():
            self.cap.release()

# ---------------- CLEANUP ----------------
def cleanup():
    print("\nCleaning up GPIO and camera...")
    rover.cleanup()
    arm.cleanup()
    detector.release()

atexit.register(cleanup)

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/video_feed')
def video_feed():
    return Response(detector.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    global automatic_mode
    data = request.get_json()
    print("[DEBUG] Received:", data)

    if 'mode' in data:
        automatic_mode = (data['mode']=='auto')
        print(f"[DEBUG] Automatic mode set to {automatic_mode}")
        if not automatic_mode:
            auto_stop_flag.set()
        else:
            auto_stop_flag.clear()
        return jsonify({'status':'mode updated','automatic':automatic_mode})

    if not automatic_mode:
        component = data.get('component')
        action = data.get('action')
        print(f"[DEBUG] Manual: {component} | {action}")

        if component=='wheels':
            wheel_map = {'wheels_forward':'forward','wheels_backward':'backward','wheels_left':'left','wheels_right':'right','wheels_stop':'stop'}
            rover_action = wheel_map.get(action)
            if rover_action:
                rover.handle_wheel_action(rover_action)
        elif component in ['arm','gripper']:
            arm_actions = {'arm_base_left':arm.move_base_left,'arm_base_right':arm.move_base_right,
                           'shoulder_left':arm.shoulder_left,'shoulder_right':arm.shoulder_right,
                           'elbow_up':arm.elbow_up,'elbow_down':arm.elbow_down,
                           'wrist_up':arm.wrist_up,'wrist_down':arm.wrist_down,
                           'gripper_open':arm.gripper_open,'gripper_close':arm.gripper_close}
            if component=='gripper':
                action = 'gripper_close' if action=='open' else 'gripper_open'
            elif component=='arm':
                action_map = {'arm_up':'elbow_up','arm_down':'elbow_down'}
                action = action_map.get(action, action)
            if action in arm_actions:
                arm_actions[action]()

    return jsonify({'status':'ok'})

# ---------------- MAIN ----------------
if __name__=='__main__':
    detector = RoseDetector()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
