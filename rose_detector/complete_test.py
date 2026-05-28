import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import tkinter as tk
from PIL import Image, ImageTk

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
        Accepts a frame, processes it, and returns the annotated frame with bounding boxes
        around detected roses.
        """
        # Preprocess frame: resize and normalize the image to match model input
        input_shape = self.input_details[0]['shape']
        img = cv2.resize(frame, (input_shape[2], input_shape[1]))  # Resize to model input size
        img = img.astype(np.float32) / 255.0  # Normalize image to [0, 1]
        img = np.expand_dims(img, axis=0)  # Add batch dimension

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()

        # Get output from the model
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Debugging: print the output data to see the detections
        print("Detection Output:", output_data)

        # Post-process: draw bounding boxes on the frame
        for det in output_data[0]:  # Assuming each detection is [x, y, w, h, confidence, class]
            x, y, w, h, conf, cls = det

            # Scale coordinates to frame size
            frame_height, frame_width = frame.shape[:2]
            x1 = int((x - w / 2) * frame_width)  # Scale to image width
            y1 = int((y - h / 2) * frame_height)  # Scale to image height
            x2 = int((x + w / 2) * frame_width)  # Scale to image width
            y2 = int((y + h / 2) * frame_height)  # Scale to image height

            # Draw bounding box if the confidence is above a threshold
            if conf > 0.3:  # Feel free to adjust the confidence threshold
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for detected object
        
        return frame  # Return the annotated frame

def update_frame():
    ret, frame = cap.read()
    if ret:
        annotated_frame = detector.detect(frame)
        
        # Convert frame to Tkinter-compatible format
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        
        # Update the Tkinter label
        label.config(image=photo)
        label.image = photo

    # Call this function again after 10 ms
    root.after(10, update_frame)

def on_closing():
    cap.release()  # Release the camera
    root.quit()

if __name__ == '__main__':
    # Open video capture device (USB camera)
    cap = cv2.VideoCapture(0)  # Use '/dev/video0' for Raspberry Pi or 0 for default camera

    if not cap.isOpened():
        print("Error: Cannot open camera")
        exit()

    detector = RoseDetector(model_path='rose_detector/model/best.tflite')  # Make sure to use the correct relative path to your model

    # Create Tkinter window
    root = tk.Tk()
    root.title("Rose Detection")

    # Set up a label widget to display the frames
    label = tk.Label(root)
    label.pack()

    # Set the window size based on the camera resolution
    root.geometry("640x480")

    # Start the frame update loop
    root.after(10, update_frame)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start Tkinter event loop
    root.mainloop()
