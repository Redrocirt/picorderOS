#!/usr/bin/python
import time
print("Loading Globals Objects")
# This module contains generally useful objects that the entire program may call on.

# This variable is used to pass information to things like progress notifications
global_notify = "PicorderOS is not active"


class preferences(object):

	#determines device ("pc", "tr108", "tr109")
	def __init__(self):
		self.version = "v0.01"
		self.author = "Developed by Chris Barrett"

		# holds the global state of the program (allows secondary modules to quit the program should we require it)
		self.status = "startup"

		# enables "PC Mode": sensors and GPIO calls are disabled.
		# Machine vitals are substituted and Luma screens use emulator
		self.pc = True


		# These two bits determine the target device (Original picorder or new version)
		# If both true the screens will fight for control!
		self.tr108 = False
		self.tr109 = True

		# testing this setting to switch between Pygame controls and gpio ones
		self.input_kb = True
		self.input_gpio = False
		self.input_cap = False

		# flags control the onboard LEDS. Easy to turn them off if need be.
		self.moire = [False]
		self.leds = [False]
		self.neopixel = [False]

		# flag controls auto ranging of graphs
		self.auto = [True]

		# chooses SPI display (0 for nokia 5110, 1 for st7735)
		self.display = "1"

		self.theme = [0]

		# enables thermal cam support
		self.tcam = False

		self.max_sensors = [9]

		# Toggles individual sensor support
		self.bme = True
		self.amg8833 = True
		self.ir_thermo = True
		self.sensehat = False
		self.envirophat = False
		self.system_vitals = True

		#selects the three sensor targets to plot
		self.sensor1 = [0]
		self.sensor2 = [1]
		self.sensor3 = [2]
		self.sensors = [self.sensor1, self.sensor2, self.sensor3]

		# this flag can be used to signal to the rest of the program that then
		# sensor arrangement has been altered, allowing the program to adjust
		# background elements if needed.
		self.sensorschanged = [False]


		self.logdata = [False]
		self.samplerate = [0]
		self.displayinterval = [0]

		# holds sensor data (issued by the sensor module at init)
		self.sensor_info = []
		self.last_status = ["startup"]

configure = preferences()

# the following function maps a value from the target range onto the desination range
def translate(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	if leftSpan == 0:
		leftSpan = 1
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan)

	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

# The following is a simple object that I can use to maintain toggled states. There's probably a better way to do it, but this is what I did!
class toggle(object):
	def __init__(self):
		self.setting = False

	def read(self):
		return self.setting

	def flip(self):
			if self.setting == True:
				self.setting = False
			else:
				self.setting = True


# The following class is to keep track of whether an item has been initiated or is to be reset. This allows me to keep track of items easily.
class initial(object):
		def __init__(self):
			self.go = 0

		def logstart(self):
			self.go = 1

		def reset(self):
			self.go = 0

		def get(self):
			return self.go

# the following class is used to make items flash by providing a timed pulse bit object.
class flash(object):
	def __init__(self):
	 self.value = 0
	 self.timelast = 0
	 self.timenow = 0

	def pulse(self):

	 if (self.timelast == 0):
		 self.timelast = time.time()

	 self.timenow = time.time()

	 if ((self.timenow - self.timelast) >= 1):

		 if (self.value == 1):
			 self.value = 0
		 else:
			 self.value = 1

		 self.timelast = time.time()

	def display(self):
	 return self.value

# The following class is to handle interval timers.
class timer(object):

	# Constructor code logs the time it was instantiated.
	def __init__(self):
		self.timeInit = time.time()
		self.logtime()

	# The following funtion returns the last logged value.
	def timestart(self):
		return self.timeInit

	# the following function updates the time log with the current time.
	def logtime(self):
		self.lastTime = time.time()

	# the following function returns the interval that has elapsed since the last log.
	def timelapsed(self):
		#print("comparing times")
		self.timeLapse = time.time() - self.lastTime
		#print("timelapse passed")
		#print(self.timeLapse)
		return self.timeLapse
