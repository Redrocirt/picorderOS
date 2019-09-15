#import pygame
import random

# Load up the image library stuff to help draw bitmaps to push to the screen
import PIL.ImageOps
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from objects import *

if not configure.pc:
	import busio
	import board
	import adafruit_amg88xx

	i2c = busio.I2C(board.SCL, board.SDA)
	amg = adafruit_amg88xx.AMG88XX(i2c)

high = 0.0
low = 0.0

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def makegrid():
	dummyvalue = []
	#
	for i in range(8):
		dummyrow = []
		for r in range(8):
			dummyrow.append(random.uniform(1.0,81.0))
		dummyvalue.append(dummyrow)

	return dummyvalue


class ThermalPixel(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.colour = (255,255,255)
		self.temp = 0

	def update(self,value,surface):
		#print(value)
		color = map(value, 1, 80, 0, 254)
		print(value)
		#color = translate(value, low, high, 0, 255)
		print(color)
		#print(color)
		surface.rectangle([(self.x, self.y), (self.x + self.w, self.y + self.h)], fill = (int(color),int(color),int(color)), outline=None)
		#pygame.draw.rect(self.surface, (color,color,color), pygame.Rect(self.x,self.y,self.w,self.h))


class ThermalRows(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

		self.pixels = []

		for i in range(8):
			self.pixels.append(ThermalPixel(self.x + (i * (w/8)), self.y, self.w / 8, self.h))

	#[10.0,10.0,10.0,10.0,10.0,10.0,10.0,10.0]
	def update(self,data,surface):
		for i in range(8):
			self.pixels[i].update(data[i], surface)



class ThermalGrid(object):

	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.h = h
		self.w = w

		self.rows = []

		for i in range(8):
			self.rows.append(ThermalRows(self.x, self.y + (i * (h/8)), self.w, self.h / 8))

	def update(self,surface):
		if not configure.pc:
			data = amg.pixels
		else:
			data = makegrid()
			#print(len(data))

		rangemax = []
		rangemin = []
		for i in range(8):
			thismax = max(data[i])
			thismin = min(data[i])
			rangemin.append(thismin)
			rangemax.append(thismax)

		high = max(rangemax)
		low = min(rangemin)

		print(high, low)
		for i in range(8):
			self.rows[i].update(data[i],surface)
		#print(rangesmax)
