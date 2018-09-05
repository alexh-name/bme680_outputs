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

def clear_list(pixels):
  print('CLEAR', len(pixels))
  pixels.clear()

# Convert string to list and check if input really was a list
def listify(str):
    _list = ast.literal_eval(str.rstrip('\n'))
    if isinstance(_list, list):
      return _list

# Add a real list to pixels, skip strings that were no list
def add_str(str, pixels):
  try:
    list = listify(str)
    add_pixel(list, pixels)
  except:
    pass

def add_pixel(list, pixels):
  pixels.append(list)
  print('ADD', list)

# Reset pixels
def reset_pixels(pixels):
  print(reset_s, len(pixels))
  clear_list(pixels)

# Restore bars
def restore_bars(pixels):
  if pixels != []:
    for pixel in pixels:
      add_pixel(pixel, pixels)
    print('RESTORE_BARS', len(pixels))

def read_fifo(fifo_file, pixels_cur, pixels_saved, pixels_bars):
  fifo = open(fifo_file, 'r')

  for line in fifo:
    s = line.strip()

    # RESET
    if s == reset_s:
      reset_pixels(pixels_cur)

    # RESET, restore bars
    if s == reset_kb_s:
      reset_pixels(pixels_cur)
      restore_bars(pixels_cur)

    # SAVE
    if s == save_s:
      pixels_saved[:] = pixels_cur.copy()
      print(save_s, len(pixels_saved))

    # BARS
    is_lo_s = s.startswith(layout_s)
    if args.layout_file != None and is_lo_s == True:
      b = s.replace(layout_s, "")
      print(layout_s, b)
      bars(b[0], b[1], b[2], b[3], pixels_cur, pixels_saved, pixels_bars)

    # FIFO LIST
    if s != reset_s and s != reset_kb_s and s != save_s and s != draw_s and is_lo_s != True:
      # Add a pixel
      add_str(s, pixels_cur)

    # DRAW
    if s == draw_s:
      # Draw pixels
      print(draw_s, len(pixels_cur))
      draw(pixels_cur)

# Read from static file
def read_file(file, pixels):
  f = open(file, "r")
  for line in f:
    add_str(line, pixels)
  f.close

# Clear pixels in a range
def blank(range_x, range_y):
  for x in range_x:
    for y in range_y:
      r, g, b = 0, 0, 0
      unicornhathd.set_pixel(x, y, r, g, b)
      print('BLANK', [x, y, r, g, b])

# Set the pixels and show them
def draw(pixels):
  valid = False
  try:
    for p in pixels:
      valid = False
      x, y, r, g, b = int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4])
      if x != '' and y != '':
        if r or g or b:
          valid = True
          unicornhathd.set_pixel(x, y, r, g, b)

    if valid:
      unicornhathd.show()

  except:
    unicornhathd.off()

# Build a pixel from layout info
def build_pixel(dict, pixels):
  for x in dict[4]:
    for y in range(dict[3]):
      pixels.append([x, y, dict[0], dict[1], dict[2]])

# Prepare info from layout
def bars(acc, air, temp, hum, pixels_cur, pixels_saved, pixels_bars):
  try:
    clear_list(pixels_cur)
    clear_list(pixels_bars)

    if len(pixels_saved) != 0:
      pixels_cur[:] = pixels_saved.copy()

    blank(range_x, range_y)

    #global colors_acc
    #global colors_air
    #global colors_temp
    #global colors_hum

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
      build_pixel(bar, pixels_cur)
      build_pixel(bar, pixels_bars)

    if air == 'v':
      for x in colors_air['xs']:
        for y in range(5):
          if y != 1:
            r, g, b = 255, 0, 0
            add_pixel([x, y, r, g, b], pixels_cur)
            add_pixel([x, y, r, g, b], pixels_bars)
    else:
      build_pixel(colors_air[air], pixels_cur)
      build_pixel(colors_air[air], pixels_bars)

  except:
    pass

def blank_full():
  width, height = unicornhathd.get_shape()
  blank(range(width), range(height))

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

    pixels_cur = []
    pixels_saved = []
    pixels_bars = []

    while True:
      read_fifo(file, pixels_cur, pixels_saved, pixels_bars)

except KeyboardInterrupt:
  unicornhathd.off()
  exit()

