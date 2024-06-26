#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2021, LaBru Systems.
drone_cargo.py Multirotor scripts
"""

from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
from pymavlink import mavutil
import time
import math
import psutil

import board
import neopixel

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Delivery Drone using Multirotor.')
parser.add_argument('--connect', default='/dev/ttyAMA0')
args = parser.parse_args()

connection_string = args.connect
sitl = None

#------ Led-------
pixels = neopixel.NeoPixel(board.D21, 58)
#walk
my_color = (55,200,230)
dim_by = 20
pos = 0
num_pixels = 58

#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
pixels.fill((255,255,255))
vehicle = connect(args.connect, baud=57600, wait_ready=True)
#57600 is the baudrate that you have set in the mission plannar or qgc
#SERIAL2_PROTOCOL = 2 (the default) to enable MAVLink 2 on the serial port.
#SERIAL2_BAUD = 57 so the flight controller can communicate with the RPi at 57600 baud.
#LOG_BACKEND_TYPE = 3 if you are using APSync to stream the dataflash log files to the RPi
# vehicle is an instance of the Vehicle class
print ("Autopilot Firmware version: %s" % vehicle.version)
print ("Global Location: %s" % vehicle.location.global_frame)
print ("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
print ("Local Location: %s" % vehicle.location.local_frame) #NED
print ("Attitude: %s" % vehicle.attitude)
print ("Velocity: %s" % vehicle.velocity)
print ("GPS: %s" % vehicle.gps_0)
print ("Groundspeed: %s" % vehicle.groundspeed)
print ("Airspeed: %s" % vehicle.airspeed)
print ("Battery: %s" % vehicle.battery)
print ("EKF OK?: %s" % vehicle.ekf_ok)
print ("Last Heartbeat: %s" % vehicle.last_heartbeat)
print ("Heading: %s" % vehicle.heading)
print ("Is Armable?: %s" % vehicle.is_armable)
print ("System status: %s" % vehicle.system_status.state)
print ("Mode: %s" % vehicle.mode.name) # settable
print ("Armed: %s" % vehicle.armed) # settable

#-------------------------Drone Script--------------------------#
def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned Location has the same `alt` value
    as `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius=6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobal(newlat, newlon,original_location.alt)

def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

def download_mission():
    """
    Download the current mission from the vehicle.
    """
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready() # wait until download is complete.

def adds_locations(aLocation): #target locations
    """
    Adds a takeoff command and four waypoint commands to the current mission. 
    The waypoints are positioned to form a square of side length 2*aSize around the specified LocationGlobal (aLocation).
    The function assumes vehicle.commands matches the vehicle mission state 
    (you must have called download at least once in the session and after clearing the mission)
    """	
    
    cmds = vehicle.commands

    print("Clear any existing commands")
    cmds.clear() 
    
    print("Define/add new commands.")
    # Add new commands. The meaning/order of the parameters is documented in the Command class. 
     
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))

    #Define the four MAV_CMD_NAV_WAYPOINT locations and add the commands
    point1 = LocationGlobalRelative(-6.9802862, 107.5700757)
    point2 = LocationGlobalRelative(-6.9801824, 107.5697377)
    point3 = LocationGlobalRelative(-6.9801291, 107.5694320)
    point4 = LocationGlobalRelative(-6.9801291, 107.5694320)
   
    #cmds.add(command(0, 0, 0, target component,seq,frame,command,current,autocontionue,param1,param2,param3,param4                 ,     x     ,     y     ,z ))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point1.lat, point1.lon, 10)) #angka terakhir altitude target
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point2.lat, point2.lon, 10))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point3.lat, point3.lon, 10))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, point3.lat, point4.lon, 10))
   
    print("Upload new commands to vehicle")
    cmds.upload()

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks ... DON'T TOUCH!!!")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print("Waiting for pidrone to initialise...")
        for i in range(5,0,-1):
            if (i % 2) == 0:
                pixels.fill((255,0,0))
            else:
                pixels.fill((0,0,0))
            time.sleep(0.1)
        time.sleep(1)

        
    print("Arming Motors")
    # VTOL should arm in QLOITER mode
    print("Switch mode To GUIDED")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print("Waiting For Arming...")
        pixels.fill((255,0,0))
        time.sleep(0.5)
        pixels.fill((0,255,0))
        time.sleep(0.5)

    print("Taking Off")
    pixels.fill((255,0,0))
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        pixels.fill((0,0,255))
        time.sleep(0.05)
        pixels.fill((0,0,0))
        time.sleep(0.05)      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            pixels.fill((0,255,0))
            print("Reached Target Altitude")
            break

#-------------------------- LED Script --------------------------#
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

#--------------- Main Program ----------------------#      
print('Create a new mission (for current location)')
adds_locations(vehicle.location.global_frame)

#-----------------------------------misi 1---------------------------#

# From Copter 3.3 you will be able to take off using a mission item. Plane must take off using a mission item (currently).
arm_and_takeoff(1)
print ("Take Off Complete")

#-- set the default speed
print ("Set Target airspeed to 7")
vehicle.airspeed = 7

for i in range(3, -1, -1): #counting down hover time before do mission
    time.sleep(1) #5sec
    print('Count To Go: '+ str(i))

for i in range(5,0,-1):
    if (i % 2) == 0:
        pixels.fill((0,0,0))
    else:
        pixels.fill((0,0,255))
    time.sleep(0.1)
    print('Fly')

print("Starting Mission 1")
# Reset mission set to first (0) waypoint
vehicle.commands.next=0 #target waypoint

# Set mode to AUTO to start mission
print("Switch mode to AUTO")
vehicle.mode = VehicleMode("AUTO")

# Monitor mission. 
# Demonstrates getting and setting the command number 
# Uses distance_to_current_waypoint(), a convenience function for finding the 
#   distance to the next waypoint.

while True:
    #---------LED------------#
    pixels[pos] = my_color
    pixels[0:] = [[max(i-dim_by,0) for i in l] for l in pixels]
    pos = (pos+1) % num_pixels
    pixels.show()
    time.sleep(0.05)
    #-------Drone-------#
    nextwaypoint=vehicle.commands.next
    print('Distance to waypoint (%s): %s Altitude: %s' % (nextwaypoint, distance_to_current_waypoint(), vehicle.location.global_relative_frame.alt))
    time.sleep(1)
    if vehicle.commands.next==3: #dummy waypoint for landing near waypoint 2
        print('Land and Drop')
        break

print("Switch mode to LAND")
vehicle.mode = VehicleMode("LAND")

while True:
    print('Altitude: %s' % (vehicle.location.global_relative_frame.alt))
    pixels.fill((0,255,0))
    time.sleep(0.5)
    pixels.fill((0,0,255))
    time.sleep(0.5)   
    if vehicle.location.global_relative_frame.alt <= 1:
        vehicle.mode = VehicleMode("ALT_HOLD")
        pixels.fill((0,255,0))
        print("Landed, Drop and wait 10s Before Take Off")
        break

#To control a servo, plug it into an empty channel on the pixhawk and use
#mission planner to set that channel as a servo channel.
#From dronekit, control it like this:
msg = vehicle.message_factory.command_long_encode(
0, 0,    # target_system, target_component
mavutil.mavlink.MAV_CMD_DO_SET_SERVO, #command
0, #confirmation
8,    # servo number
1700,          # servo position between 1000 and 2000
0, 0, 0, 0, 0)    # param 3 ~ 7 not used

# send command to vehicle
print("Release Package Drop")
vehicle.send_mavlink(msg)
pixels.fill((255,0,255))


#----------------------------------misi 2-----------------------------------#

for i in range(5, -1, -1): #counting down time in ground before take off
    if (i % 2) == 0:
        pixels.fill((255,0,0))
    else:
        pixels.fill((0,0,0))
    time.sleep(1) #10sec
    print('Count To Take Off: '+ str(i))

arm_and_takeoff(10)
print ("Take Off Complete")

#-- set the default speed
print ("Set Target airspeed to 7")
vehicle.airspeed = 7

for i in range(3, -1, -1): #counting down hover time before do mission
    time.sleep(1) #5sec
    print('Count To Go: '+ str(i))

for i in range(5,0,-1):
    if (i % 2) == 0:
        pixels.fill((0,0,0))
    else:
        pixels.fill((0,0,255))
    time.sleep(0.1)
    print('Fly')

print("Switch mode to RTL")
vehicle.mode = VehicleMode("SMART_RTL") #default altitude rtl 15m
while True:
    #---------LED------------#
    pixels[pos] = my_color
    pixels[0:] = [[max(i-dim_by,0) for i in l] for l in pixels]
    pos = (pos+1) % num_pixels
    pixels.show()
    time.sleep(0.05)
    #-------Drone---------#
    print("Return to home, Altitude: %s" % vehicle.location.global_relative_frame.alt)
    if vehicle.location.global_relative_frame.alt <= 0.5 : #point to vehicle.close
        print("Landed")
        print("DISARMING MOTORS")
        break
    time.sleep(1)

#Close vehicle object before exiting script
print("Congratulation! Mission Complete")
vehicle.close()
pixels.fill((0,255,0))
time.sleep(3)
pixels.fil((0,0,0))
print('Drone turn off')

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()
