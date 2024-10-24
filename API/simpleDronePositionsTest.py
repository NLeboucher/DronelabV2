from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

# The URI of the Crazyflie to connect to
uri = 'radio://0/28/2M/E7E7E7E703'

# Step 1: Create a Log Configuration
log_config = LogConfig(name="Position", period_in_ms=100)
log_config.add_variable('stateEstimate.x', 'float')
log_config.add_variable('stateEstimate.y', 'float')
log_config.add_variable('stateEstimate.z', 'float')

# Step 2: Callback for handling incoming log data
def position_callback(timestamp, data, logconf):
    print(f"X: {data['stateEstimate.x']}, Y: {data['stateEstimate.y']}, Z: {data['stateEstimate.z']}")

log_config.data_received_cb.add_callback(position_callback)

# Step 3: Establish a connection with the Crazyflie
with SyncCrazyflie(link_uri=uri) as scf:
    cf = scf.cf

    # Step 4: Registering the log configuration with the Crazyflie
    cf.log.add_config(log_config)

    # Step 5: Start logging
    if log_config.valid:
        log_config.start()

        # Keep the script running to receive log data
        print("Logging data from Crazyflie. Press Ctrl+C to stop...")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass

        log_config.stop()
    else:
        print("LogConfig not valid!")
