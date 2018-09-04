# 'xs' is the range of x-coordinates to draw on

# IAQ color codes provided by Bosch
# g: Good air
# a: Average air
# l: Little bad air
# b: Bad air
# w: Worse air
# v: Very bad air

colors_air = {
  'xs': range(1,2),
  'g': (0,227,0,1),
  'a': (255,255,0,2),
  'l': (255,125,0,3),
  'b': (255,0,0,4),
  'w': (153,0,75,5),
  'v': (0,0,0,0)
}

# Temperature
# h: Hot
# w: Warm
# g: Good
# c: Cold
# f: Freezing

colors_temp = {
  'xs': range(2,3),
  'h': (255,0,0,5),
  'w': (255,128,128,4),
  'g': (255,255,255,3),
  'c': (128,128,255,2),
  'f': (0,0,255,1)
}

# Humidity
# v: Very humid
# h: Humid
# g: Good
# a: Arid

colors_hum = {
  'xs': range(3,4),
  'v': (0,0,255,5),
  'h': (128,128,255,4),
  'g': (255,255,255,3),
  'a': (255,128,128,2)
}

colors_acc = {
  'xs': range(0,1),
  '0': (255,0,0,1),
  '1': (255,125,0,2),
  '2': (255,255,0,3),
  '3': (0,227,0,4)
}

