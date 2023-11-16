import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.swarm import Swarm

def VerifyConnection(scf, uri):
    """
    Verify the connection to a Crazyflie drone.

    Parameters:
    - scf (SyncCrazyflie): SyncCrazyflie object.
    - uri (str): URI of the drone to verify.
    """
    try:
        scf.open_link()
        print(f"Connected to {uri}")
    except Exception as e:
        print(f"Failed to connect to {uri}: {e}")

def main():
    # Define the drone URIs as a list
    uris = [
        "radio://0/80/2M/E7E7E7E701",
        "radio://0/27/2M/E7E7E7E702",
        "radio://0/28/2M/E7E7E7E703"
    ]

    # Create a Swarm object and use parallel_safe to verify connections in parallel
    # with Swarm(uris) as swarm:
    #     swarm.parallel_safe(VerifyConnection)
    with SyncCrazyflie(uris[2], cf=Crazyflie(rw_cache='./cache')) as scf:
        VerifyConnection(scf, uris[0])

if __name__ == "__main__":
    main()
