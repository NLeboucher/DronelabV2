import cflib
from cflib.crazyflie import Crazyflie
cflib.crtp.init_drivers()
address = 'E7E7E7E70'
channel = 27
datarate = '2M'

uri1 = f'radio://0/{channel}/{datarate}/{address+"1"}'
uri2 = f'radio://0/{channel}/{datarate}/{address+"2"}'
uri3 = f'radio://0/{channel}/{datarate}/{address+"3"}'
print(uri1,uri2,uri3)

cf = Crazyflie(link=uri1,ro_cache=None, rw_cache=None)
print(cf)