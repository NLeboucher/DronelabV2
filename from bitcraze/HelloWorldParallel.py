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

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

drones = []
def activate_mellinger_controller(scf, use_mellinger):
    controller = 1
    if use_mellinger:
        controller = 2
    scf.cf.param.set_value('stabilizer.controller', controller)


def run_shared_sequence(scf):
    global drones
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


    # activate_mellinger_controller(scf, False)

    # box_size = 1
    # flight_time = 2

    # commander = scf.cf.high_level_commander

    # commander.takeoff(1.0, 2.0)
    # time.sleep(3)

    # commander.go_to(box_size, 0, 0, 0, flight_time, relative=True)
    # time.sleep(flight_time)

    # commander.go_to(0, box_size, 0, 0, flight_time, relative=True)
    # time.sleep(flight_time)

    # commander.go_to(-box_size, 0, 0, 0, flight_time, relative=True)
    # time.sleep(flight_time)

    # commander.go_to(0, -box_size, 0, 0, flight_time, relative=True)
    # time.sleep(flight_time)

    # commander.land(0.0, 2.0)
    # time.sleep(2)

    # commander.stop()


uris = {
    'radio://0/28/2M/E7E7E7E703',
    'radio://0/80/2M/E7E7E7E701',
    'radio://0/27/2M/E7E7E7E702',
    # Add more URIs if you want more copters in the swarm
}

if __name__ == '__main__':
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    swarm = Swarm(uris, factory)
    try:
        swarm.open_links()
    except Exception as e:
        print(f"tried connection to swarm but:{e}")
    #swarm.reset_estimators()
    swarm.parallel(run_shared_sequence)
    print(drones)
    print([drone._link_uri for drone in drones])

