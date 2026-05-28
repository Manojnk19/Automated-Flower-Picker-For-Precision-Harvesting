from rover_control import RoverControl
import time

if __name__ == '__main__':
    rover = RoverControl()
    try:
        print("Rover control test started.")
        while True:
            print("Start")
            time.sleep(5)
            print("Forward")
            rover.forward()
            time.sleep(1)
            rover.stop()
            time.sleep(4)

            print("Left")
            rover.left()
            time.sleep(1)
            rover.stop()
            time.sleep(4)

            print("Right")
            rover.right()
            time.sleep(1)
            rover.stop()
            time.sleep(4)

            print("Backward")
            rover.backward()
            time.sleep(1)
            rover.stop()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting and cleaning up GPIO...")
        rover.cleanup()
