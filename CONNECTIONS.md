# 🌹 Rose Harvester - GPIO Connections

## 🧭 Summary of GPIO Usage

| Function             | GPIO Pins Used | Connected To                       | Notes |
|----------------------|----------------|-----------------------------------|-------|
| Rover Movement       | 5, 6, 12, 13, 20, 21 | L298N Motor Driver Inputs       | 2 pins per motor pair: IN1/IN2 → Left, IN3/IN4 → Right |
| Arm Base Servo       | 4             | MG995 360° Servo       | Continuous rotation servo |
| Shoulder Servo       | 17             | MG996S 180° Servo      | Angle control 0–180° |
| Elbow Servo          | 27             | MG996g 180° Servo      | Continuous rotation servo |
| Wrist Servo          | 22             | SG90 180° Servo        | Optional wrist movement |
| Gripper Servo        | 23             | SG90 180° Servo             | Opens/closes to cut flower |
| Reserved / Future Use| 22, 24, 25     | Optional sensors (e.g., ultrasonic, IR) | Can be used for obstacle detection or automation |

---

## 🔌 Power Supply Notes

- **Servos** should be powered from an **external 5V source** (capable of 4–6A if all servos move simultaneously).  
- **Raspberry Pi 5V pins** should **not** directly drive servos. Use ULN2803 as a buffer.  
- **L298N**: Connect motor supply (Vs) to 7–12V, GND common with RPi.  

---

## ⚡ Motor Driver Wiring (L298N)

| Motor | L298N Pins | Connection |
|-------|------------|-----------|
| Left Motors  | IN1 / IN2 | GPIO 5 / 6  |
| Right Motors | IN3 / IN4 | GPIO 12 / 13 |
| ENA          | ENA        | GPIO20 / 5V / PWM if speed control |
| ENB          | ENB        | GPIO21 / 5V / PWM if speed control |
| Vcc          | 12V        | External battery (7–12V) |
| GND          | GND        | Common ground with RPi and battery |

---

## 🖇️ Servo Wiring via ULN2803

| Servo       | ULN2803 Input Pin | ULN2803 Output | GPIO Pin | Notes |
|-------------|-----------------|----------------|----------|-------|
| Base        | IN1             | OUT1           | 4        | MG995 360° |
| Shoulder    | IN2             | OUT2           | 17       | MG996S 180° |
| Elbow       | IN3             | OUT3           | 27       | MG995 360° |
| Wrist       | IN4             | OUT4           | 22       | SG90 180° |
| Gripper     | IN5             | OUT5           | 23       | SG90 180° |

---

## 📝 Notes

1. **Common Ground**: Connect all grounds (RPi, ULN2803, servos, L298N) together.  
2. **Signal Levels**: ULN2803 allows safe level shifting and buffering for the RPi GPIO pins.  
3. **PWM Frequency**: Standard 50Hz for all hobby servos.  
4. **Testing**: Always test one component at a time to avoid overcurrent.  

---

**Project Structure Reference**

```bash
rose-harvester/
│
├─ rose-detector/ # YOLOv5 or TFLite flower detection
├─ rover-navigation/ # Rover movement code
├─ arm-navigation/ # Base, Shoulder, Elbow, Wrist servo code
└─ gripper-cutter/ # Gripper control code
```