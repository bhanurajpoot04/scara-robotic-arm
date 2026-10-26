# Pin map

Derived from the pin definitions in the original `SCARA_Robot.ino` (HowToMechatronics), which this build follows.
Header names are the CNC Shield V3 silkscreen labels. **Check them against your own board.**

## Stepper drivers (A4988 on CNC Shield V3)

| Driver slot | STEP | DIR | Joint (original design) | Steps per unit in original code |
|---|---|---|---|---|
| X | D2 | D5 | J1 (shoulder) | 44.44 steps / degree |
| Y | D3 | D6 | J2 (elbow) | 35.56 steps / degree |
| Z | D4 | D7 | J3 (wrist rotation) | 10 steps / degree |
| A (spindle pins) | D12 | D13 | Z lift (lead screw) | 100 steps / Z unit |

Link lengths used in the original kinematics: L1 = 228 mm, L2 = 136.5 mm.

## Limit switches (homing)

| Switch | Pin | Axis |
|---|---|---|
| LS1 | D11 | J1 |
| LS2 | D10 | J2 |
| LS3 | D9 | J3 |
| LS4 | A3 | Z lift |

The original firmware sets all four as `INPUT_PULLUP` and homes each axis until the pin reads HIGH, so the
switches are wired **normally-closed to GND** (the pin reads LOW until the switch opens when pressed).
Homing order in the original firmware: Z lift, J3, J2, J1.

## Gripper servo (MG996R)

| Signal | Pin |
|---|---|
| PWM | A0 (pulse range 600-2500 us in the original code) |
| Power | 5 V and GND |

In the original GUI the gripper slider runs 0-100 and is sent as servo angle = value + 50 (50-150 deg).
An MG996R can draw a lot of current when it stalls. If the Arduino resets or the servo jitters, power the servo
from a separate 5-6 V supply and join its ground with the Arduino ground.

## Power and communication

- 12 V DC supply (a 10 A unit was used) to the CNC Shield power terminal, for the motors.
- Arduino Uno connects to the laptop over USB (serial, 115200 baud).
- Set each A4988 current limit (Vref) for your motor's rated current and your driver board's sense resistor, as per the
  driver datasheet. Power off before plugging or unplugging motors or drivers.
