"""
Example of how to read the Lighthouse base station geometry and
calibration memory from a Crazyflie
"""
import logging
from threading import Event

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import LighthouseMemHelper
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class ReadMem:
    def __init__(self, uri):
        self._event = Event()

        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            helper = LighthouseMemHelper(scf.cf)

            helper.read_all_geos(self._geo_read_ready)
            self._event.wait()

            self._event.clear()

            helper.read_all_calibs(self._calib_read_ready)
            self._event.wait()

    def _geo_read_ready(self, geo_data):
        for id, data in geo_data.items():
            print('---- Geometry for base station', id + 1)
            data.dump()
            print()
        self._event.set()

    def _calib_read_ready(self, calib_data):
        for id, data in calib_data.items():
            print('---- Calibration data for base station', id + 1)
            data.dump()
            print()
        self._event.set()


if __name__ == '__main__':
    # URI to the Crazyflie to connect to
    URI1 = "radio://0/80/2M/E7E7E7E701"
    URI2 = "radio://0/27/2M/E7E7E7E702"
    URI3 = "radio://0/28/2M/E7E7E7E703"
    URI1 = uri_helper.uri_from_env(default=URI1)
    URI2 = uri_helper.uri_from_env(default=URI2)
    URI3 = uri_helper.uri_from_env(default=URI3)

    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    # ReadMem(URI1)
    # ReadMem(URI2)
    ReadMem(URI3)