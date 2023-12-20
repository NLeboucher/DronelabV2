import logging
import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

# Set the URI of the Crazyflie you want to connect to
uri = "radio://0/27/2M/E7E7E7E702"

# Initialize the logging framework
logging.basicConfig(level=logging.ERROR)

# Function to connect to the Crazyflie and perform some basic operations
def connect_to_crazyflie(uri):
    # Create a SyncCrazyflie instance
    with SyncCrazyflie(uri) as scf:
        # Access the Crazyflie API through the SyncCrazyflie instance (scf.cf)
        cf = scf.cf

        # Start communication with the Crazyflie
        print(f"Connection link is open: {scf.is_link_open()}")
        #cf.open_link()

        # Your code to interact with the Crazyflie goes here

        # For example, print the Crazyflie firmware version
        

        # Stop communication with the Crazyflie
        cf.close_link()

if __name__ == "__main__":
    # Initialize the Crazyflie SDK
    cflib.crtp.init_drivers(enable_debug_driver=False)

    # Call the function to connect to the Crazyflie
    connect_to_crazyflie(uri)