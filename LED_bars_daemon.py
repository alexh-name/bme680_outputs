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

# Clear pixels
def clear_pixels(pixels):
  print(reset_s, len(pixels))
  pixels.clear()

# Blank drawn pixels in a range
def blank_range(range_x, range_y):
  for x in range_x:
    for y in range_y:
      r, g, b = 0, 0, 0
      print('BLANK', [x, y, r, g, b])
      unicornhathd.set_pixel(x, y, r, g, b)

def blank_full():
  width, height = unicornhathd.get_shape()
  blank_range(range(width), range(height))


# Adding pixels
def add_pixel(list, pixels):
  print('ADD', list)
  pixels.append(list)

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


# Copy list, e.g. to restore bars
def copy_pixels(pixels_from, pixels_to):
  if len(pixels_from) != 0:
    for pixel in pixels_from:
      add_pixel(pixel, pixels_to)

# Overwrite list with list
def overwrite_pixels(pixels_from, pixels_to):
  print('OVERWRITE', len(pixels_to), 'with',  len(pixels_from))
  pixels_to[:] = pixels_from.copy()


# Build a pixel from layout info
def build_pixels(dict, pixels):
  for x in dict[4]:
    for y in range(dict[3]):
      pixels.append([x, y, dict[0], dict[1], dict[2]])

# Prepare info from layout
def bars(str, pixels_cur, pixels_saved, pixels_bars):
  try:
    # Remove prefix
    b = str.replace(layout_s, '')
    print(layout_s, b)

    # Override current pixels with saved pixels, to avoid progressive grow of pixels
    # with each update on bars
    clear_pixels(pixels_cur)
    if len(pixels_saved) != 0:
      pixels_cur[:] = pixels_saved.copy()

    # Make sure bars range is blanked
    blank_range(bars_range_x, bars_range_y)

    acc, air, temp, hum = b[0], b[1], b[2], b[3]
    # Now we know the key for r, g, b, y, so we can also add x into the final dict
    colors_acc[acc].append(colors_acc['xs'])
    colors_air[air].append(colors_air['xs'])
    colors_temp[temp].append(colors_temp['xs'])
    colors_hum[hum].append(colors_hum['xs'])

    # Temporary local list of bar pixels
    pixels = []

    # Make a list of the finals dicts to iterate over them
    bars = []
    bars.append(colors_acc[acc])
    bars.append(colors_temp[temp])
    bars.append(colors_hum[hum])

    # Special case for worst kind of air quality.
    # Displays a red '!'
    # Otherwise just add to the list like the others.
    if air != 'v':
      bars.append(colors_air[air])
    else:
      for x in colors_air['xs']:
        for y in range(5):
          if y != 1:
            r, g, b = 255, 0, 0
            add_pixel([x, y, r, g, b], pixels)

    # Build copy pixels from the dicts according to layout.
    # Also save them in pixels_bars, so they can be retrieved after blanking
    for bar in bars:
      build_pixels(bar, pixels)
    copy_pixels(pixels, pixels_cur)
    overwrite_pixels(pixels, pixels_bars)

  except:
    pass


# Write the pixels and show them
def draw(pixels):
  print('DRAW', len(pixels))
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


# Read lists from static file
def read_file(file, pixels):
  f = open(file, 'r')
  for line in f:
    add_str(line, pixels)
  f.close


# Read lists and commands from named pipe
def read_fifo(fifo_file, pixels_cur, pixels_saved, pixels_bars):
  fifo = open(fifo_file, 'r')

  for line in fifo:
    s = line.strip()

    # RESET
    if s == reset_s:
      reset_pixels(pixels_cur)

    # RESET, restore bars
    if s == reset_kb_s:
      overwrite_pixels(pixels_bars, pixels_cur)

    # SAVE
    if s == save_s:
      overwrite_pixels(pixels_cur, pixels_saved)

    # BARS
    is_lo_s = s.startswith(layout_s)
    if args.layout_file != None and is_lo_s == True:
      bars(s, pixels_cur, pixels_saved, pixels_bars)

    # FIFO LIST
    if s != reset_s and s != reset_kb_s and s != save_s and s != draw_s and is_lo_s != True:
      # Add a pixel
      add_str(s, pixels_cur)

    # DRAW
    if s == draw_s:
      # Draw pixels
      draw(pixels_cur)


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

