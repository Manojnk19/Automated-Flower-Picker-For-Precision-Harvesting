# ==================== arm_control.py ====================
import RPi.GPIO as GPIO
import time

class ArmControl:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # Servo pins
        self.base_pin = 4
        self.shoulder_pin = 17
        self.elbow_pin = 27
        self.wrist_pin = 22
        self.gripper_pin = 23

        # Setup pins for PWM
        self.servos = {}
        for pin in [self.base_pin, self.shoulder_pin, self.elbow_pin, self.wrist_pin, self.gripper_pin]:
            GPIO.setup(pin, GPIO.OUT)
            self.servos[pin] = GPIO.PWM(pin, 50)  # 50 Hz
            self.servos[pin].start(0)

        # Current angles
        self.shoulder_angle = 130
        self.elbow_angle = 120
        self.wrist_angle = 90
        self.gripper_angle = 0

    # ---------------- Base Controls ----------------
    def move_base_right(self, duration=0.1):
        self._move_servo(self.base_pin, 70, duration)

    def move_base_left(self, duration=0.1):
        self._move_servo(self.base_pin, 110, duration)

    # ---------------- Shoulder Controls ----------------
    def shoulder_left(self, increment=5):
        self.shoulder_angle = min(180, self.shoulder_angle + increment)
        self._move_servo(self.shoulder_pin, self.shoulder_angle, 0.3)

    def shoulder_right(self, decrement=5):
        self.shoulder_angle = max(0, self.shoulder_angle - decrement)
        self._move_servo(self.shoulder_pin, self.shoulder_angle, 0.3)

    # ---------------- Elbow Controls ----------------
    def elbow_down(self, increment=5):
        self.elbow_angle = min(180, self.elbow_angle + increment)
        self._move_servo(self.elbow_pin, self.elbow_angle, 0.3)

    def elbow_up(self, decrement=5):
        self.elbow_angle = max(0, self.elbow_angle - decrement)
        self._move_servo(self.elbow_pin, self.elbow_angle, 0.3)

    # ---------------- Wrist Controls ----------------
    def wrist_up(self, increment=5):
        self.wrist_angle = min(90, self.wrist_angle + increment)
        self._move_servo(self.wrist_pin, self.wrist_angle, 0.3)

    def wrist_down(self, decrement=5):
        self.wrist_angle = max(0, self.wrist_angle - decrement)
        self._move_servo(self.wrist_pin, self.wrist_angle, 0.3)

    # ---------------- Gripper Controls ----------------
    def gripper_open(self):
        print("gripper open")
        self.gripper_angle = 90
        self._move_servo(self.gripper_pin, self.gripper_angle, 0.3)

    def gripper_close(self):
        print("gripper close")
        self.gripper_angle = 10
        self._move_servo(self.gripper_pin, self.gripper_angle, 0.3)

    # ---------------- Internal Method ----------------
    def _move_servo(self, pin, angle, duration):
        duty = 2 + (angle / 18)  # Convert angle to duty cycle
        self.servos[pin].ChangeDutyCycle(duty)
        time.sleep(duration)
        self.servos[pin].ChangeDutyCycle(0)

    def cleanup(self):
        for pwm in self.servos.values():
            pwm.stop()
        GPIO.cleanup()
