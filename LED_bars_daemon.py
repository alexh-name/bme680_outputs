#!/usr/bin/env python

# Daemon, who will take a string of 4 characters via a FIFO.
# $ echo 3vwh > /tmp/unicornhat_bars.fifo
# Each character corresponding to a key in layout dict.
# Order of characters:
# 1. accuracy,
# 2. air quality,
# 3. temperature,
# 4. humidity

import os
import atexit
import unicornhathd

unicornhathd.rotation(90)
unicornhathd.brightness(0.1)
fifo_file = '/tmp/unicornhat_bars.fifo'
# Layout dict:
execfile('./LED_bars_layout.py')

#-----

width, height = unicornhathd.get_shape()
valid = False

def draw(x,dict):
  for y in range(dict[3]):
    global valid
    r, g, b = dict[0],dict[1],dict[2]
    if r or g or b:
      valid = True
      #print(x,valid)
      unicornhathd.set_pixel(x, y, r, g, b)
    else:
      #print(x,valid)
      valid = False

def bars(acc,air,temp,hum):      
  try:
    color_acc = colors_acc[acc]
    color_air = colors_air[air]
    color_temp = colors_temp[temp]
    color_hum = colors_hum[hum]

    # blank pixels first. should be better than a whole uni.off().
    for x in range(width):
      for y in range(height):
        r, g, b = 0,0,0
        unicornhathd.set_pixel(x, y, r, g, b)

    for x in colors_acc['xs']:
      draw(x,color_acc)

    if air == 'v':
      for x in colors_air['xs']:
        for y in range(5):
          if y != 1:
            r, g, b = 255,0,0
            unicornhathd.set_pixel(x, y, r, g, b)
    else:
      for x in colors_air['xs']:
        draw(x,color_air)

    for x in colors_temp['xs']:
      draw(x,color_temp)

    for x in colors_hum['xs']:
      draw(x,color_hum)

    if valid:
      unicornhathd.show()

  except:
    unicornhathd.off()

# Set up the FIFO
os.mkfifo(fifo_file)

# Make sure to clean up after ourselves
def cleanup():
  os.remove(fifo_file)

atexit.register(cleanup)

# Go into reading loop
while True:
  with open(fifo_file, 'r') as fifo:
    for line in fifo:
      s = line.strip()
      bars(s[0],s[1],s[2],s[3])

