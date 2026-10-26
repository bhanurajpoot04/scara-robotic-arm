/*
  gesture_serial_controller.ino  --  REFERENCE FIRMWARE (not verified on hardware)

  Receives the simple text commands sent by software/gesture_control/scaracv.py
  and jogs the SCARA arm's steppers / gripper servo.

  STATUS: written for this repository to match the protocol used by scaracv.py.
  It uses the same pins and libraries as the original HowToMechatronics SCARA
  firmware, but this exact sketch has NOT been run on the arm. Test with the
  motors unloaded or the arm in a safe pose, and keep a hand on the power switch.

  Protocol (115200 baud, each command ends with '\n'):
    X40   X-40   jog the X-slot stepper  +40 / -40 steps   (J1)
    Y40   Y-40   jog the Y-slot stepper                      (J2)
    Z40   Z-40   jog the Z-slot stepper                      (J3)
    A40   A-40   jog the A-slot stepper                      (Z lift)
    G1           gripper OPEN
    G0           gripper CLOSE
  Replies (printed back over serial):
    "X moving 40 steps..." then "X done. Current position: 40"
    "Unknown command: <text>" for anything else

  Axis letters follow the CNC Shield V3 driver slots (X, Y, Z, A). In the
  original SCARA design these drive J1, J2, J3 and the Z lift respectively.

  Libraries: AccelStepper (Mike McCauley), Servo (built in).

  NOTE: this sketch does NOT home the arm. Power it on with the arm in a known,
  safe pose; step positions are counted from that pose.
*/
#include <AccelStepper.h>
#include <Servo.h>

// ---- Pins (same as the original SCARA firmware on CNC Shield V3) ----
AccelStepper stepX(AccelStepper::DRIVER, 2, 5);    // J1   STEP=D2  DIR=D5
AccelStepper stepY(AccelStepper::DRIVER, 3, 6);    // J2   STEP=D3  DIR=D6
AccelStepper stepZ(AccelStepper::DRIVER, 4, 7);    // J3   STEP=D4  DIR=D7
AccelStepper stepA(AccelStepper::DRIVER, 12, 13);  // Z lift STEP=D12 DIR=D13
const uint8_t ENABLE_PIN  = 8;    // CNC Shield V3 driver enable (active LOW)
const uint8_t GRIPPER_PIN = A0;

// ---- Tunables (conservative starting values - adjust for your arm) ----
const float MAX_SPEED_STEPS_S   = 1000;  // original firmware allowed up to 4000
const float ACCEL_STEPS_S2      = 1000;
const long  MAX_JOG_PER_COMMAND = 400;   // clamp, protects against a bad command
const int   GRIPPER_OPEN_DEG    = 150;   // GUI slider 0-100 maps to 50-150 deg
const int   GRIPPER_CLOSE_DEG   = 50;    // adjust to your gripper's travel

Servo gripper;
String line;

AccelStepper* stepperFor(char axis) {
  switch (axis) {
    case 'X': return &stepX;
    case 'Y': return &stepY;
    case 'Z': return &stepZ;
    case 'A': return &stepA;
  }
  return nullptr;
}

void jog(char axis, long steps) {
  AccelStepper* s = stepperFor(axis);
  steps = constrain(steps, -MAX_JOG_PER_COMMAND, MAX_JOG_PER_COMMAND);
  Serial.print(axis);
  Serial.print(F(" moving "));
  Serial.print(steps);
  Serial.println(F(" steps..."));
  s->move(steps);
  s->runToPosition();               // blocking; fine for short jog bursts
  Serial.print(axis);
  Serial.print(F(" done. Current position: "));
  Serial.println(s->currentPosition());
}

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;
  char c = toupper(cmd.charAt(0));

  if (c == 'G' && cmd.length() >= 2) {
    char v = cmd.charAt(1);
    if (v == '1') {
      gripper.write(GRIPPER_OPEN_DEG);
      Serial.println(F("Gripper OPEN"));
      return;
    }
    if (v == '0') {
      gripper.write(GRIPPER_CLOSE_DEG);
      Serial.println(F("Gripper CLOSE"));
      return;
    }
  } else if (stepperFor(c) != nullptr && cmd.length() >= 2) {
    jog(c, cmd.substring(1).toInt());
    return;
  }

  Serial.print(F("Unknown command: "));
  Serial.println(cmd);
}

void setup() {
  Serial.begin(115200);

  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);    // enable the A4988 drivers

  AccelStepper* all[] = {&stepX, &stepY, &stepZ, &stepA};
  for (AccelStepper* s : all) {
    s->setMaxSpeed(MAX_SPEED_STEPS_S);
    s->setAcceleration(ACCEL_STEPS_S2);
  }

  gripper.attach(GRIPPER_PIN, 600, 2500);   // same pulse range as the original
  gripper.write(GRIPPER_OPEN_DEG);
  delay(500);

  Serial.println(F("Stepper test ready."));
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') {
      if (line.length()) handleCommand(line);
      line = "";
    } else if (line.length() < 24) {
      line += ch;
    }
  }
}
