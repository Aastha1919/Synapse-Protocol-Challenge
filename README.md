# Synapse-Protocol-Challenge
Industrial Edge device polling simulation using Modbus RTU.
Project Overview
This repository contains a Python-based Edge polling solution designed to interface with industrial assets (Inverters/BESS controllers) via the Modbus RTU protocol. The system is designed to handle raw register data, apply engineering scaling factors, and output structured JSON for upstream cloud processing.
System Components
`mainprj.py`: The primary Edge Client (Master) logic. It manages the serial connection, register polling, and data transformation.
`in.py`: A dedicated Mock Server (Slave) used for local integration testing. It simulates real-time register fluctuations (Voltage, Current, Power) to verify client-side parsing.
`socat` Utility': Since this is a software simulation, `socat` is used to create a virtual null-modem bridge (`/tmp/ttyS0` <-> `/tmp/ttyS1`), allowing the two Python scripts to communicate over virtual serial TTYs

Data Transformation & Scaling
Industrial Modbus registers often store values as integers to save bandwidth. This implementation handles:
Scaling : Applies a `0.1` multiplier to convert raw integers to standard units (V, A, kW, kWh).
Signed Integers : Register 40002 (System Current) is treated as a 16-bit signed integer using Two's Complement logic to support bi-directional current flow (charging/discharging).
JSON Schema:Outputs a flat JSON object to ensure compatibility with standard IoT telemetry ingestion engines.

2. Fault Tolerance & Reliability
In industrial environments, serial communication is prone to electromagnetic interference (EMI) and physical disconnection. 
Exception Handling:The client is wrapped in a robust `try-except` structure to catch `ModbusException` and `SerialException`.
Auto-Recovery: Instead of terminating on a "Port Not Found" or "Timeout" error, the script logs the fault and enters a retry loop. It will automatically re-establish the handshake once the physical (or virtual) link is restored.

Setup & Execution

**Environment Requirements:**
* Python 3.9+
* pip install pymodbus pyserial
* sudo apt install socat

Initialize Virtual Bridge (Terminal 1):**
   ```bash
   socat -d -d PTY,link=/tmp/ttyS0,raw,echo=0 PTY,link=/tmp/ttyS1,raw,echo=0

Launch Mock Inverter (Terminal 2):
python3 in.py

Launch Edge Poller (Terminal 3):
python3 mainprj.py

Evaluation Output:
{
    "system_voltage_V": 230.5,
    "system_current_A": 12.8,
    "active_power_kW": 2.95,
    "daily_energy_yield_kWh": 150.2
}
