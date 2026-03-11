import time
import random
import threading
import logging
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# --- PyModbus Version Compatibility ---
# Detects if you are using the new v3.12+ (Device) or the old v3.x (Slave)
try:
    from pymodbus.datastore import ModbusDeviceContext as ContextWrapper
except ImportError:
    from pymodbus.datastore import ModbusSlaveContext as ContextWrapper

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger()

def update_registers(context):
    device_context = context[0]
    
    register_block = 3 
    starting_address = 0

    while True:
        voltage = random.randint(2250, 2350)
        power = random.randint(20, 50)
        energy = random.randint(1500, 1510)
        
        raw_current = random.randint(-50, 150)
        if raw_current < 0:
            current = 65536 + raw_current 
        else:
            current = raw_current

        new_values = [voltage, current, power, energy]

        device_context.setValues(register_block, starting_address, new_values)
        log.info(f"Updated Registers internally: Voltage={voltage/10}V, Current={raw_current/10}A")
        time.sleep(2)

def run_live_mock_inverter():
    # Initialize using the dynamically imported wrapper
    store = ContextWrapper(hr=ModbusSequentialDataBlock(0, [0, 0, 0, 0]))
    
    # PyModbus also changed the keyword arguments for the Server Context.
    # This tries all known valid keywords depending on your version.
    try:
        context = ModbusServerContext(slaves=store, single=True)
    except TypeError:
        try:
            context = ModbusServerContext(devices=store, single=True)
        except TypeError:
            context = ModbusServerContext(device_ids=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Synapse Challenge'
    identity.ModelName = 'Live Mock Inverter'

    update_thread = threading.Thread(target=update_registers, args=(context,), daemon=True)
    update_thread.start()

    print("Starting LIVE Mock Modbus Server on /tmp/ttyS0...")
    
    StartSerialServer(
        context=context, 
        identity=identity, 
        port='/tmp/ttyS0', 
        baudrate=9600
    )

if __name__ == "__main__":
    run_live_mock_inverter()
