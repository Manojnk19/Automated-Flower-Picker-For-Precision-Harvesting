import RPi.GPIO as GPIO
import time

class RoverControl:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # L298N pins updated as per user input
        self.in1 = 6    # GPIO6, pin 31
        self.in2 = 5    # GPIO5, pin 29
        self.in3 = 20   # GPIO20, pin 38
        self.in4 = 21   # GPIO21, pin 40
        self.ena = 12   # GPIO12, pin 32
        self.enb = 13   # GPIO13, pin 33

        # Setup pins as output BEFORE initializing PWM
        for pin in [self.in1, self.in2, self.in3, self.in4, self.ena, self.enb]:
            GPIO.setup(pin, GPIO.OUT)

        # Initialize PWM for speed control
        self.pwm_frequency = 100  # Hz
        self.duty_cycle = 50      # 50% speed

        self.ena_pwm = GPIO.PWM(self.ena, self.pwm_frequency)
        self.enb_pwm = GPIO.PWM(self.enb, self.pwm_frequency)

        self.ena_pwm.start(0)
        self.enb_pwm.start(0)

    # ---------------- Rover Movements ----------------
    def forward(self, duration=0.5):
        # Left and right clockwise
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)
        self.ena_pwm.ChangeDutyCycle(self.duty_cycle)
        self.enb_pwm.ChangeDutyCycle(self.duty_cycle)
        time.sleep(duration)
        self.stop()

    def backward(self, duration=0.5):
        # Left and right anticlockwise
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)
        self.ena_pwm.ChangeDutyCycle(self.duty_cycle)
        self.enb_pwm.ChangeDutyCycle(self.duty_cycle)
        time.sleep(duration)
        self.stop()

    def right(self, duration=0.5):
        # right motor backward, left motor forward
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)
        self.ena_pwm.ChangeDutyCycle(self.duty_cycle)
        self.enb_pwm.ChangeDutyCycle(self.duty_cycle)
        time.sleep(duration)
        self.stop()

    def left(self, duration=0.5):
        # right motor forward, left motor backward
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)
        self.ena_pwm.ChangeDutyCycle(self.duty_cycle)
        self.enb_pwm.ChangeDutyCycle(self.duty_cycle)
        time.sleep(duration)
        self.stop()

    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)
        self.ena_pwm.ChangeDutyCycle(0)
        self.enb_pwm.ChangeDutyCycle(0)

    def handle_wheel_action(self, action):
        if action == 'forward':
            self.forward()
        elif action == 'backward':
            self.backward()
        elif action == 'left':
            self.left()
        elif action == 'right':
            self.right()
        elif action == 'stop':
            self.stop()

    def cleanup(self):
        self.stop()
        self.ena_pwm.stop()
        self.enb_pwm.stop()
        GPIO.cleanup()