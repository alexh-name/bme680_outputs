#!/usr/bin/env python
#
# Convert an image to 16x16 lists of RGB pixels:
# [x, y, r, g, b]

#import os
from sys import argv
try:
    from PIL import Image
except ImportError:
    exit('This script requires the pillow module')

width = 16
height = 16

img_file = argv[1]
img = Image.open(img_file)

#array_file = os.path.splitext(img_file)[0] + '.txt'

pixels = []

try:

  # IMAGE
  for o_x in range(int(img.size[0]/width)):
    for o_y in range(int(img.size[1]/height)):

       for x in range(width):
         for y in range(height):
           pixel = img.getpixel(((o_x*width)+y,(o_y*height)+x))
           r, g, b = int(pixel[0]),int(pixel[1]),int(pixel[2])
           if r or g or b:
             pixels.append([x, y, r, g, b])

  for pixel in pixels:
   print(pixel)

  #with open(array_file, 'w') as f:
  #    for item in pixels:
  #        f.write("%s\n" % item)
  #f.close
  #####

except:
  exit()

