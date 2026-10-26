# Firmware

| Sketch | Used for | Status |
|---|---|---|
| `gesture_serial_controller/` | Demo 2: receives the text commands from `software/gesture_control/scaracv.py` (`X40`, `A-40`, `G1`, ...) | Reference sketch written for this repo. **Not verified on the arm.** |
| Original `SCARA_Robot.ino` | Demo 1: works with the Processing GUI (homing, kinematics, save / run positions) | By Dejan Nedelkovski, [HowToMechatronics](https://howtomechatronics.com/projects/scara-robot-how-to-build-your-own-arduino-based-robot/). Not redistributed here, download it from the tutorial page. |

Both use the same pins (see [`hardware/pin-map.md`](../hardware/pin-map.md)) and the
[AccelStepper](http://www.airspayce.com/mikem/arduino/AccelStepper/) library.

The original `SCARA_Robot.ino` expects comma-separated data from the GUI, so it will not
understand the gesture commands. Flash one sketch at a time depending on which demo you run.
