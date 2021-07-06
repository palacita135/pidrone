from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time

# Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='127.0.0.1:14550')
args = parser.parse_args()

# Connect to the Vehicle
print ('Connecting to pidrone4 on: %s' % args.connect)
vehicle = connect(args.connect, baud=57600, wait_ready=True)
#57600 is the baudrate that you have set in the mission plannar or qgc
#SERIAL2_PROTOCOL = 2 #(the default) to enable MAVLink 2 on the serial port.
#SERIAL2_BAUD = 57600 #so the flight controller can communicate with the RPi at 57600 baud.
#LOG_BACKEND_TYPE = 3 if you are using APSync to stream the dataflash log files to the RPi
# vehicle is an instance of the Vehicle class
print ("Autopilot Firmware version: %s" % vehicle.version)
#print ("Autopilot capabilities (supports ftp): %s" % vehicle.capabilities.ftp)
print ("Global Location: %s" % vehicle.location.global_frame)
print ("Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
print ("Local Location: %s" % vehicle.location.local_frame) #NED
print ("Attitude: %s" % vehicle.attitude)
print ("Velocity: %s" % vehicle.velocity)
print ("GPS: %s" % vehicle.gps_0)
print ("Groundspeed: %s" % vehicle.groundspeed)
print ("Airspeed: %s" % vehicle.airspeed)
print ("Gimbal status: %s" % vehicle.gimbal)
print ("Battery: %s" % vehicle.battery)
print ("EKF OK?: %s" % vehicle.ekf_ok)
print ("Last Heartbeat: %s" % vehicle.last_heartbeat)
print ("Rangefinder: %s" % vehicle.rangefinder)
print ("Rangefinder distance: %s" % vehicle.rangefinder.distance)
print ("Rangefinder voltage: %s" % vehicle.rangefinder.voltage)
print ("Heading: %s" % vehicle.heading)
print ("Is Armable?: %s" % vehicle.is_armable)
print ("System status: %s" % vehicle.system_status.state)
print ("Mode: %s" % vehicle.mode.name) # settable
print ("Armed: %s" % vehicle.armed) # settable

# Function to arm and then takeoff to a user specified altitude
def arm_and_takeoff(aTargetAltitude):

  print ("Basic pre-arm checks")
  # Don't let the user try to arm until autopilot is ready
  while not vehicle.is_armable:
    print ("Waiting for pidrone4 to initialise...")
    time.sleep(1)
        
  print ("Arming motors")
  # Copter should arm in GUIDED mode
  vehicle.mode    = VehicleMode("GUIDED")
  vehicle.armed   = True

  while not vehicle.armed:
    print ("Waiting for arming...")
    time.sleep(1)

  print ("Taking Off")
  vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

  # Check that vehicle has reached takeoff altitude
  while True:
    print (" Altitude:"), vehicle.location.global_relative_frame.alt
    #Break and return from function just below target altitude.        
    if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95: 
      print ("Reached target altitude")
      break
    time.sleep(1)

# Initialize the takeoff sequence to 10m
arm_and_takeoff(10)

print ("Take off complete")

# Hover for 10 seconds
print ("Hover For 10s")
for i in range(10, -1, -1): #hitung mundur/hover (waktu, detik keberapa beresnya, pengurangan waktu)
    time.sleep(1) #selang waktu 10 sampe 1
    print(' waktu hover: '+ str(i))

print ("Now let's land")
vehicle.mode = VehicleMode("LAND")
while True:
    vehicle.location.global_relative_frame.alt is not 0.5
    print(" Altitude: %s" % vehicle.location.global_relative_frame.alt)
    if vehicle.location.global_relative_frame.alt <= 0.5 : #patokan untuk menuju vehicle.close
        print("congratulation! mission done")
        break
    time.sleep(1)

#--- Return To Launch
#print ("Return To Home")
#vehicle.mode = VehicleMode("RTL")

# Close vehicle object
#print ("Mission Complete")
vehicle.close()
