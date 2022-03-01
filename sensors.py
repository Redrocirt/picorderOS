from objects import *
import time
from plars import *
import math
import numpy

# the following is a sensor module for use with the PicorderOS
print("Loading Unified Sensor Module")


if not configure.pc:
	import os

if configure.bme:
	import adafruit_bme680
	import busio as io



if configure.sensehat:
	# instantiates and defines paramaters for the sensehat

	from sense_hat import SenseHat

	# instantiate a sensehat object,
	sense = SenseHat()

	# Initially clears the LEDs once loaded
	sense.clear()

	# Sets the IMU Configuration.
	sense.set_imu_config(True,False,False)

	# Prepares an array of 64 pixel triplets for the Sensehat moire display
	moire=[[0 for x in range(3)] for x in range(64)]


if configure.envirophat:
	from envirophat import light, weather, motion, analog

# support for the MLX90614 IR Thermo
if configure.ir_thermo:
	import busio as io
	import adafruit_mlx90614

# These imports are for the Sin and Tan waveform generators
if configure.system_vitals:
	import psutil
	import math

if configure.pocket_geiger:
	from PiPocketGeiger import RadiationWatch

if configure.amg8833:
	import adafruit_amg88xx
	import busio
	import board
	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)


# An object to store each sensor value and context.
class Fragment(object):

	__slots__ = ('value','mini','maxi','dsc','sym','dev','timestamp')

	def __init__(self,mini,maxi,dsc,sym,dev):
		self.mini = mini
		self.maxi = maxi
		self.dsc = dsc
		self.dev = dev
		self.sym = sym
		self.value = 47

	# Sets the value and timestamp for the fragment.
	def set(self,value, timestamp):

		self.value = value

		self.timestamp = timestamp

	# Returns all the data for the fragment.
	def get(self):
		return [self.value, self.mini, self.maxi, self.dsc, self.sym, self.dev, self.timestamp]

	# Returns only the info constants for this fragment
	def get_info(self):
		return [self.mini, self.maxi, self.dsc, self.sym, self.dev]

class Sensor(object):
	# sensors should check the configuration flags to see which sensors are
	# selected and then if active should poll the sensor and append it to the
	# sensor array.

	def __init__(self):

		#set up the necessary info for the sensors that are active.

		# create a simple reference for the degree symbol since we use it a lot
		self.deg_sym = '\xB0'

		self.generators = False

		# add individual sensor module parameters below.
		#0				1			2		3		4
		#info = (lower range, upper range, unit, symbol)
		#'value','min','max','dsc','sym','dev','timestamp'


		# testing:
		# data fragments (objects that contain the most recent sensor value,
		# plus its context) are objects called Fragment().
		if configure.system_vitals:

			self.step = 0.0
			self.step2 = 0.0
			self.steptan = 0.0
			totalmem = float(psutil.virtual_memory().total) / 1024

			self.cputemp = Fragment(0, 100, "CpuTemp", self.deg_sym + "c", "RaspberryPi")
			self.cpuperc = Fragment(0,100,"CpuPercent","%","Raspberry Pi")
			self.virtmem = Fragment(0,totalmem,"VirtualMemory","b","RaspberryPi")
			self.bytsent = Fragment(0,100000,"BytesSent","b","RaspberryPi")
			self.bytrece = Fragment(0, 100000,"BytesReceived","b","RaspberryPi")

			if self.generators:
				self.sinewav = Fragment(-100,100,"SineWave", "","RaspberryPi")
				self.tanwave = Fragment(-500,500,"TangentWave", "","RaspberryPi")
				self.coswave = Fragment(-100,100,"CosWave", "","RaspberryPi")
				self.sinwav2 = Fragment(-100,100,"SineWave2", "","RaspberryPi")

		if configure.sensehat:
			self.ticks = 0
			self.onoff = 1

			# instantiate a sensehat object,
			self.sense = SenseHat()
			# Initially clears the LEDs once loaded
			self.sense.clear()
			# Sets the IMU Configuration.
			self.sense.set_imu_config(True,False,False)
			# activates low light conditions to not blind the user.
			self.sense.low_light = True

			self.sh_temp = Fragment(0,65,"Thermometer",self.deg_sym + "c", "sensehat")
			self.sh_humi = Fragment(20,80,"Hygrometer", "%", "sensehat")
			self.sh_baro = Fragment(260,1260,"Barometer","hPa", "sensehat")
			self.sh_magx = Fragment(-500,500,"MagnetX","G", "sensehat")
			self.sh_magy = Fragment(-500,500,"MagnetY","G", "sensehat")
			self.sh_magz = Fragment(-500,500,"MagnetZ","G", "sensehat")
			self.sh_accx = Fragment(-500,500,"AccelX","g", "sensehat")
			self.sh_accy = Fragment(-500,500,"AccelY","g", "sensehat")
			self.sh_accz = Fragment(-500,500,"AccelZ","g", "sensehat")

		if configure.ir_thermo:
			i2c = io.I2C(configure.PIN_SCL, configure.PIN_SDA, frequency=100000)
			self.mlx = adafruit_mlx90614.MLX90614(i2c)

			self.irt_ambi = Fragment(0,80,"IR ambient [mlx]",self.deg_sym + "c")
			self.irt_obje = Fragment(0,80,"IR object [mlx]",self.deg_sym + "c")

		if configure.envirophat: # and not configure.simulate:

			self.ep_temp = Fragment(0,65,"Thermometer",self.deg_sym + "c","Envirophat")
			self.ep_colo = Fragment(20,80,"Colour", "RGB","Envirophat")
			self.ep_baro = Fragment(260,1260,"Barometer","hPa","Envirophat")
			self.ep_magx = Fragment(-500,500,"Magnetomer X","G","Envirophat")
			self.ep_magy = Fragment(-500,500,"Magnetomer Y","G","Envirophat")
			self.ep_magz = Fragment(-500,500,"Magnetomer Z","G","Envirophat")
			self.ep_accx = Fragment(-500,500,"Accelerometer X (EP)","g","Envirophat")
			self.ep_accy = Fragment(-500,500,"Accelerometer Y (EP)","g","Envirophat")
			self.ep_accz = Fragment(-500,500,"Accelerometer Z (EP)","g","Envirophat")

		if configure.bme:
			# Create library object using our Bus I2C port
			i2c = io.I2C(configure.PIN_SCL, configure.PIN_SDA)
			self.bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76, debug=False)

			self.bme_temp = Fragment(-40,85,"Thermometer",self.deg_sym + "c", "BME680")
			self.bme_humi = Fragment(0,100,"Hygrometer", "%", "BME680")
			self.bme_press = Fragment(300,1100,"Barometer","hPa", "BME680")
			self.bme_voc = Fragment(300000,1100000,"VOC","KOhm", "BME680")
			self.voc_procc = subprocess.Popen(['./bsec_bme680'], stdout=subprocess.PIPE)

			if configure.bme_bsec:
				self.bme_bsec = Fragment(-40,85,"Quality",self.deg_sym + "Q", "BME680")

		if configure.pocket_geiger:
			self.radiat = Fragment(0.0, 10000.0, "Radiation", "urem/hr", "pocketgeiger")
			self.radiation = RadiationWatch(configure.PG_SIG,configure.PG_NS)
			self.radiation.setup()

		if configure.amg8833:
			self.amg_high = Fragment(0.0, 80.0, "IRHigh", self.deg_sym + "c", "amg8833")
			self.amg_low = Fragment(0.0, 80.0, "IRLow", self.deg_sym + "c", "amg8833")

		configure.sensor_info = self.get_all_info()


	def get_all_info(self):
		info = self.get()

		allinfo = []
		for fragment in info:
			thisfrag = [fragment.dsc,fragment.dev,fragment.sym, fragment.mini, fragment.maxi]
			allinfo.append(thisfrag)
		return allinfo

	def sin_gen(self):
		wavestep = math.sin(self.step)
		self.step += .1
		return wavestep

	def tan_gen(self):
		wavestep = math.tan(self.steptan)
		self.steptan += .1
		return wavestep

	def sin2_gen(self, offset = 0):
		wavestep = math.sin(self.step2)
		self.step2 += .05
		return wavestep

	def cos_gen(self, offset = 0):
		wavestep = math.cos(self.step)
		self.step += .1
		return wavestep


	def get(self):

		#sensorlist holds all the data fragments to be handed to plars.
		sensorlist = []

		#timestamp for this sensor get.
		timestamp = time.time()



		if configure.bme:

			self.bme_temp.set(self.bme.temperature,timestamp)
			self.bme_humi.set(self.bme.humidity,timestamp)
			self.bme_press.set(self.bme.pressure,timestamp)
			self.bme_voc.set(self.bme.gas / 1000,timestamp)

			sensorlist.extend((self.bme_temp,self.bme_humi,self.bme_press, self.bme_voc))

		if configure.sensehat:

			magdata = sense.get_compass_raw()
			acceldata = sense.get_accelerometer_raw()

			self.sh_temp.set(sense.get_temperature(),timestamp)
			self.sh_humi.set(sense.get_humidity(),timestamp)
			self.sh_baro.set(sense.get_pressure(),timestamp)
			self.sh_magx.set(magdata["x"],timestamp)
			self.sh_magy.set(magdata["y"],timestamp)
			self.sh_magz.set(magdata["z"],timestamp)
			self.sh_accx.set(acceldata['x'],timestamp)
			self.sh_accy.set(acceldata['y'],timestamp)
			self.sh_accz.set(acceldata['z'],timestamp)

			sensorlist.extend((self.sh_temp, self.sh_baro, self.sh_humi, self.sh_magx, self.sh_magy, self.sh_magz, self.sh_accx, self.sh_accy, self.sh_accz))

		if configure.pocket_geiger:

			data = self.radiation.status()
			rad_data = float(data["uSvh"])

			# times 100 to convert to urem/h
			self.radiat.set(rad_data*100, timestamp)

			sensorlist.append(self.radiat)

		if configure.amg8833:
			data = numpy.array(amg.pixels)

			high = numpy.max(data)
			low = numpy.min(data)

			self.amg_high.set(high,timestamp)
			self.amg_low.set(low,timestamp)

			sensorlist.extend((self.amg_high, self.amg_low))

		if configure.envirophat:
			self.rgb = light.rgb()
			self.analog_values = analog.read_all()
			self.mag_values = motion.magnetometer()
			self.acc_values = [round(x, 2) for x in motion.accelerometer()]

			self.ep_temp.set(weather.temperature(),timestamp)
			self.ep_colo.set(light.light(),timestamp)
			self.ep_baro.set(weather.pressure(unit='hpa'), timestamp)
			self.ep_magx.set(self.mag_values[0],timestamp)
			self.ep_magy.set(self.mag_values[1],timestamp)
			self.ep_magz.set(self.mag_values[2],timestamp)
			self.ep_accx.set(self.acc_values[0],timestamp)
			self.ep_accy.set(self.acc_values[1],timestamp)
			self.ep_accz.set(self.acc_values[2],timestamp)

			sensorlist.extend((self.ep_temp, self.ep_baro, self.ep_colo, self.ep_magx, self.ep_magy, self.ep_magz, self.ep_accx, self.ep_accy, self.ep_accz))

		# provides the basic definitions for the system vitals sensor readouts
		if configure.system_vitals:

			if not configure.pc:
				f = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
				t = float(f[0:2] + "." + f[2:])
			else:
				t = float(47)

			# update each fragment with new data and mark the time.
			self.cputemp.set(t,timestamp)
			self.cpuperc.set(float(psutil.cpu_percent()),timestamp)
			self.virtmem.set(float(psutil.virtual_memory().available * 0.0000001),timestamp)
			self.bytsent.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp)
			self.bytrece.set(float(psutil.net_io_counters().bytes_recv * 0.00001),timestamp)

			if self.generators:
				self.sinewav.set(float(self.sin_gen()*100),timestamp)
				self.tanwave.set(float(self.tan_gen()*100),timestamp)
				self.coswave.set(float(self.cos_gen()*100),timestamp)
				self.sinwav2.set(float(self.sin2_gen()*100),timestamp)

			# load the fragments into the sensorlist
			sensorlist.extend((self.cputemp, self.cpuperc, self.virtmem, self.bytsent, self.bytrece))

			if self.generators:
				 sensorlist.extend((self.sinewav, self.tanwave, self.coswave, self.sinwav2))



		configure.max_sensors[0] = len(sensorlist)

		if len(sensorlist) < 1:
			print("NO SENSORS LOADED")

		return sensorlist

class MLX90614():

	MLX90614_RAWIR1=0x04
	MLX90614_RAWIR2=0x05
	MLX90614_TA=0x06
	MLX90614_TOBJ1=0x07
	MLX90614_TOBJ2=0x08

	MLX90614_TOMAX=0x20
	MLX90614_TOMIN=0x21
	MLX90614_PWMCTRL=0x22
	MLX90614_TARANGE=0x23
	MLX90614_EMISS=0x24
	MLX90614_CONFIG=0x25
	MLX90614_ADDR=0x0E
	MLX90614_ID1=0x3C
	MLX90614_ID2=0x3D
	MLX90614_ID3=0x3E
	MLX90614_ID4=0x3F

	comm_retries = 5
	comm_sleep_amount = 0.1

	def __init__(self, address=0x5a, bus_num=1):
		self.bus_num = bus_num
		self.address = address
		self.bus = smbus.SMBus(bus=bus_num)

	def read_reg(self, reg_addr):
		err = None
		for i in range(self.comm_retries):
			try:
				return self.bus.read_word_data(self.address, reg_addr)
			except IOError as e:
				err = e
				#"Rate limiting" - sleeping to prevent problems with sensor
				#when requesting data too quickly
				sleep(self.comm_sleep_amount)

		#By this time, we made a couple requests and the sensor didn't respond
		#(judging by the fact we haven't returned from this function yet)
		#So let's just re-raise the last IOError we got
		raise err

	def data_to_temp(self, data):
		temp = (data*0.02) - 273.15
		return temp

	def get_amb_temp(self):
		data = self.read_reg(self.MLX90614_TA)
		return self.data_to_temp(data)

	def get_obj_temp(self):
		data = self.read_reg(self.MLX90614_TOBJ1)
		return self.data_to_temp(data)

def threaded_sensor():

	sensors = Sensor()
	sensors.get()
	configure.buffer_size[0] = configure.graph_size[0]*len(configure.sensor_info)
	configure.sensor_ready[0] = True

	timed = timer()


	while not configure.status == "quit":

		if timed.timelapsed() > configure.samplerate[0]:

			timed.logtime()
			data = sensors.get()
			plars.update(data)
