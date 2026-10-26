"""List available serial ports so you can set SERIAL_PORT in scaracv.py.

Usage:  python list_ports.py
"""
from serial.tools import list_ports

ports = list(list_ports.comports())
if not ports:
    print("No serial ports found. Check the USB cable and the Arduino driver.")
for p in ports:
    print(f"{p.device}  -  {p.description}")
