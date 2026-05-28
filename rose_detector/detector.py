import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

class RoseDetector:
    def __init__(self, model_path='rose_detector/model/best.tflite'):
        # Load the TFLite model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def detect(self, frame):
        """
        Accepts a frame (from Flask app or camera), processes it, and returns the annotated frame
        with bounding boxes drawn around detected roses.
        """
        try:
            # Preprocess frame: resize and normalize
            input_shape = self.input_details[0]['shape']
            img = cv2.resize(frame, (input_shape[2], input_shape[1]))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], img)
            self.interpreter.invoke()

            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

            # Post-process detections
            for det in output_data[0]:
                if len(det) < 6:
                    continue
                x, y, w, h, conf, cls = det
                if conf > 0.3:
                    h_frame, w_frame = frame.shape[:2]
                    x1 = int((x - w / 2) * w_frame)
                    y1 = int((y - h / 2) * h_frame)
                    x2 = int((x + w / 2) * w_frame)
                    y2 = int((y + h / 2) * h_frame)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Rose {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            return frame, True

        except Exception as e:
            print(f"Detection Error: {e}")
            return frame, False
