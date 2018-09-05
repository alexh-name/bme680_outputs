#!/usr/bin/env python
#
# Draw on the Unicorn HAT HD providing a list of pixels.
# You can provide a file for one time drawing
# or run as daemon to write through a named pipe.
#
# Each pixel should be provided as a list of values, one per line:
# '[x, y, r, g, b]'.
#
# You can tell the daemon to save, reset or draw the list by writing
# save_s, reset_s or draw_s
# to the pipe.
#
# For e.g. dynamic bars you can provide a layout file. Values for the bars can be written
# via the named pipe, prefixed with layout_s.
# $ echo LAYOUT3vwh > /tmp/unicornhat.fifo
# Each character corresponding to a key in layout dict.
# Order of characters:
# 1. accuracy,
# 2. air quality,
# 3. temperature,
# 4. humidity
# reset_kb_s will reset the list of pixels while reserving the last built bars.

import ast
import os
import atexit
import argparse
import unicornhathd

#--------------------------------
unicornhathd.rotation(90)
unicornhathd.brightness(0.1)

reset_s='RESET'
reset_kb_s='RESET_KB'
draw_s='DRAW'
layout_s='LAYOUT'
save_s='SAVE'
#---------------------------------

parser = argparse.ArgumentParser()

parser.add_argument('-f', dest='list_file',
                    help='File containing a saved list', metavar='FILE')
parser.add_argument('-p', dest='fifo_file',
                    help='FIFO named pipe receiving lists', metavar='FILE')
parser.add_argument('-l', dest='layout_file',
                    help='Layout file containing more complex drawing instructions',
                    metavar='FILE')
args = parser.parse_args()

width, height = unicornhathd.get_shape()
pixels = []
pixels_saved = []
pixels_bars = []
valid = False

# Convert string to list and check if input really was a list
def listify(str):
    _list = ast.literal_eval(str.rstrip('\n'))
    if isinstance(_list, list):
      return _list

# Add a real list to pixels, skip strings that were no list
def add_str(str):
  try:
    list = listify(str)
    add_pixel(pixels,list)
  except:
    pass

def add_pixel(list_list,list):
  list_list.append(list)
  print('ADD: ', list)

# Reset pixels
def reset_pixels():
  print(reset_s,len(pixels))
  del pixels[:]

# Restore bars
def restore_bars():
  for pixel in pixels_bars:
    add_pixel(pixels,pixel)
  print('RESTORE_BARS',len(pixels))

def read_fifo(fifo_file):
  with open(fifo_file, 'r') as fifo:
    for line in fifo:
      s = line.strip()

      # RESET
      if s == reset_s:
        reset_pixels()

      # RESET, restore bars
      if s == reset_kb_s:
        reset_pixels()
        restore_bars()

      # SAVE
      if s == save_s:
        pixels_saved = pixels.copy()
        print(save_s,len(pixels_saved))

      # LAYOUT
      is_lo_s = s.startswith(layout_s)
      if args.layout_file != None and is_lo_s == True:
        b = s.replace(layout_s,"")
        print(layout_s,b)
        bars(b[0],b[1],b[2],b[3])

      # FIFO LIST
      if s != reset_s and s != reset_kb_s and s != save_s and s != draw_s and is_lo_s != True:
        # Add a pixel
        add_str(s)

      # DRAW
      if s == draw_s:
        # Draw pixels
        print(draw_s,len(pixels))
        draw()

# Read from static file
def read_file(file):
  f = open(file, "r")
  for line in f:
    add_str(line)
  f.close

# Clear pixels in a range
def blank(range_x, range_y):
  for x in range_x:
    for y in range_y:
      r, g, b = 0,0,0
      unicornhathd.set_pixel(x, y, r, g, b)
      print('BLANK: ', [x, y, r, g, b])

# Set the pixels and show them
def draw():
  try:
    for p in pixels:
      valid = False
      x, y, r, g, b = int(p[0]),int(p[1]),int(p[2]),int(p[3]),int(p[4])
      if x != '' and y != '':
        if r or g or b:
          valid = True
          unicornhathd.set_pixel(x, y, r, g, b)

    if valid:
      unicornhathd.show()

  except:
    unicornhathd.off()

# Build a pixel from layout info
def build_pixel(dict):
  for x in dict[4]:
    for y in range(dict[3]):
      r, g, b = dict[0],dict[1],dict[2]
      add_pixel(pixels,[x, y, r, g, b])
      add_pixel(pixels_bars,[x, y, r, g, b])

# Prepare info from layout
def bars(acc,air,temp,hum):
  try:
    del pixels_bars[:]
    pixels = pixels_saved.copy()
    blank(range_x,range_y)

    # Now we know the key for r, g, b, y, so we can also add x into the final dict
    colors_acc[acc].append(colors_acc['xs'])
    colors_air[air].append(colors_air['xs'])
    colors_temp[temp].append(colors_temp['xs'])
    colors_hum[hum].append(colors_hum['xs'])

    bars = []
    bars.append(colors_acc[acc])
    bars.append(colors_temp[temp])
    bars.append(colors_hum[hum])

    for bar in bars:
      build_pixel(bar)

    if air == 'v':
      for x in colors_air['xs']:
        for y in range(5):
          if y != 1:
            r, g, b = 255,0,0
            add_pixel(pixels,[x, y, r, g, b])
            add_pixel(pixels_bars,[x, y, r, g, b])
    else:
      build_pixel(colors_air[air])

  except:
    pass

def blank_full():
  blank(range(width),range(height))

# MAIN
try:
  # tabula rasa
  blank_full()

  # Static file
  if args.list_file != None:
    read_file(args.list_file)
    draw()

  # Layout
  if args.layout_file != None:
    exec(open(args.layout_file).read())

  # FIFO
  if args.fifo_file != None:
    file = args.fifo_file
    # Set up the FIFO
    os.mkfifo(file)

    # Make sure to clean up after ourselves
    def cleanup():
      os.remove(file)

    atexit.register(cleanup)

    while True:
      read_fifo(file)

except KeyboardInterrupt:
  unicornhathd.off()
  exit()

