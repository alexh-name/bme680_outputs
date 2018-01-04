#!/usr/bin/env python

# for use with Pimoroni's unicornhatHD

from sys import argv
import unicornhathd

unicornhathd.rotation(90)
unicornhathd.brightness(0.1)

# IAQ color codes provided by Bosch
# g: Good air
# a: Average air
# l: Little bad air
# b: Bad air
# w: Worse air
# v: Very bad air

colors_air = {
  'g': (0,227,0,15),
  'a': (255,255,0,8),
  'l': (255,125,0,6),
  'b': (255,0,0,4),
  'w': (153,0,75,2),
  'v': (0,0,0,0)
}

# Temperature
# h: Hot
# w: Warm
# g: Good
# c: Cold
# F: Freezing

colors_temp = {
  'h': (255,0,0,15),
  'w': (255,128,128,11),
  'g': (255,255,255,8),
  'c': (128,128,255,5),
  'f': (0,0,255,2)
}

# Humidity
# v: Very humid
# h: Humid
# g: Good
# a: Arid

colors_hum = {
  'v': (0,0,255,15),
  'h': (128,128,255,11),
  'g': (255,255,255,8),
  'a': (255,128,128,4)
}

color_air = colors_air[argv[1]]
color_temp = colors_temp[argv[2]]
color_hum = colors_hum[argv[3]]

width, height = unicornhathd.get_shape()

def draw(x,dict):
  for y in range(dict[3]):
    r, g, b = dict[0],dict[1],dict[2]
    if r or g or b:
      unicornhathd.set_pixel(x, y, r, g, b)
    else:
      valid = False
      
try:
  # blank pixels first. should be better than a whole uni.off().
  for x in range(width):
    for y in range(height):
      r, g, b = 0,0,0
      unicornhathd.set_pixel(x, y, r, g, b)

  valid = True
  for x in [1, 2, 3, 4]:
    draw(x,color_air)

  # in case of very bad air, draw an exclamation mark
  if argv[1] == 'v':
    for x in [2,3]:
      for y in range(14):
        if y != 0 and y != 3:
          r, g, b = 255,0,0
          unicornhathd.set_pixel(x, y, r, g, b)

  for x in [6, 7, 8, 9]:
    draw(x,color_temp)

  for x in [11, 12, 13, 14]:
    draw(x,color_hum)

  if valid:
    unicornhathd.show()

except:
  unicornhathd.off()

