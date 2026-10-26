# Attribution

This project is built on the open-source SCARA robot by **Dejan Nedelkovski** of HowToMechatronics.

| Item | Original source | Used here as |
|---|---|---|
| 3D model and STL files | [Tutorial page](https://howtomechatronics.com/projects/scara-robot-how-to-build-your-own-arduino-based-robot/) links to the Cults3D listing | Purchased by the team from Cults3D, printed and assembled. The files stay under the design's Cults license and are not included in this repo. Photos of our own prints are shared |
| `SCARA_Robot.ino` firmware | Same tutorial page (header: "by Dejan, www.HowToMechatronics.com") | Used for Demo 1. Not included in this repo |
| `GUI_for_SCARA_Robot.pde` (Processing GUI) | Same tutorial page | Used for Demo 1. Not included in this repo |
| Circuit diagram, assembly guide | Same tutorial page and [video](https://youtu.be/1QHJksTrk8s) | Followed for the build. This repo has its own wiring diagram drawn from the firmware's pin definitions |

The original firmware uses the [AccelStepper](http://www.airspayce.com/mikem/arduino/AccelStepper/) library by Mike McCauley.

## Original work in this repository

- `software/gesture_control/scaracv.py`: gesture classification and serial control with OpenCV and MediaPipe (team of 3)
- `firmware/gesture_serial_controller/`: reference firmware that speaks the gesture script's command protocol
- `hardware/` and `docs/`: pin map, BOM, wiring overview and this document
- `media/`: photos and demo clip of our own build

If you reuse the designs or code, please credit the original author and check the license terms on the original pages.
