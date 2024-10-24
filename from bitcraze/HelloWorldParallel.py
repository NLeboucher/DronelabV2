# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2019 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
Simple example of a swarm using the High level commander.

The swarm takes off and flies a synchronous square shape before landing.
The trajectories are relative to the starting positions and the Crazyflies can
be at any position on the floor when the script is started.

This example is intended to work with any absolute positioning system.
It aims at documenting how to use the High Level Commander together with
the Swarm class.
"""
import time
import os
path = os.getcwd()
print(path)
import cflib.crtp
# from cflib.crazyflie.swarm import CachedCfFactory
from swarm import Swarm
from swarm import CachedCfFactory

class Velocity():
    Vx:str
    Vy:str
    Vz:str
    yaw_rate:float | None = None

drones = []
def activate_mellinger_controller(scf, use_mellinger):
    controller = 1
    if use_mellinger:
        controller = 2
    scf.cf.param.set_value('stabilizer.controller', controller)


def run_shared_sequence(scf,args_dict):
    global drones
    print(f"args_dict:{args_dict}")
    print(f"Connecting to {scf._link_uri}")
    print(scf.is_link_open())
    if(scf.is_link_open()):
        drones.append(scf)
    else:
        scf.open_link()
        if(scf.is_link_open()):
            drones.append(scf)
            scf.close_link()
        else:
            print(f"Connection failed for {scf._link_uri}")




URIS = [
    'radio://0/28/2M/E7E7E7E703',
    # 'radio://0/80/2M/E7E7E7E701',
    'radio://0/27/2M/E7E7E7E702',
    # Add more URIs if you want more copters in the swarm
]
if __name__ == '__main__':
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(ro_cache='./cache',rw_cache='./cache')
    SWARM = Swarm(URIS, factory)
    V = Velocity(Vx=0,Vy=0,Vz=0,yaw_rate=0)
    args={URIS[0]:{"use_mellinger":V},URIS[1]:{"use_mellinger":V}} 
    print(f"OPENING LINKS with {args}")
    try:
        SWARM.open_links()
        print("OPENED LINKS")
    except Exception as e:
        print(f"tried connection to swarm but:{e}")
    #swarm.reset_estimators()
    a = time.time()
    SWARM.parallel_safe(run_shared_sequence,args_dict=args)
    print(drones)
    print([drone._link_uri for drone in drones])
    SWARM.close_links()
    print(time.time()-a)
