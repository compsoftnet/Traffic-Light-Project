#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2021 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 30    #traffic light
    pNE = 1. / 11    #traffic light
    pEN = 1. / 10
    pNW = 1. / 11
    pWN = 1. / 11     #traffic light 
    pEE = 1. / 10     #traffic light
    with open("pro.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeEW" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" \
guiShape="emergency"/>
        <vType id="typeNE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeEN" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNW" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeWN" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeEE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>

        <route id="right" edges="e10 e9 e8" />
        <route id="left" edges="e1 e2 e3 e4 e5" />
        <route id="up" edges="e10 e11 e18 e13" />
        <route id="side" edges="e1 e2 e12 e13" />
        <route id="sides" edges="e14 e16 e5" />
        <route id="curve" edges="e1 e6 e7 e8" />
        <route id="down" edges="e14 e15 e17 e7 e8" />""", file=routes)
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" color="1,0,0" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNE:
                print('    <vehicle id="down_%i" type="typeNE" route="down" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEN:
                print('    <vehicle id="side_%i" type="typeEN" route="side" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNW:
                print('    <vehicle id="sides_%i" type="typeNW" route="sides" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pWN:
                print('    <vehicle id="up_%i" type="typeWN" route="up" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEE:
                print('    <vehicle id="curve_%i" type="typeEE" route="curve" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                lastVeh = i
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NEEWWN
#     <tlLogic id="4" type="static" programID="0" offset="0">
#        <phase duration="27" state="GGGrrrr"/>
#        <phase duration="3"  state="yyyrrrr"/>
#        <phase duration="27" state="rrrGGrr"/>
#        <phase duration="3"  state="rrryyrr"/>
#        <phase duration="27" state="rrrrrGG"/>
#        <phase duration="3"  state="rrrrryy"/>
    
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 3 where EW has green
    traci.trafficlight.setPhase("4", 2)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if traci.trafficlight.getPhase("4") == 2:
            # we are not already switching
            if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
                # there is a vehicle from the east, switch
                traci.trafficlight.setPhase("4", 3)
            else:
                # otherwise try to keep green for NEWN
                traci.trafficlight.setPhase("4", 2)
        step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "pro.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()