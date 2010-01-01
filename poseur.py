#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Poseur is a simple presentation viewer.

Copyright (C) 2010 Christian Stigen Larsen
Distributed under the (modified) BSD license.

http://github.com/cslarsen/poseur
"""

import sys
import getopt
import math

version   = '0.0.1'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'
license   = 'Distributed under the (modified) BSD license'

slides = [
  'What is Poseur?',
  '- A simple presentation software',
  '- Written in Python',
  '- Free and open source',
]

options = {
  'fullscreen': False,
  'verbose':    False,
  'width': 1024,
  'height': 768,
}

try:
  import pyglet
  from pyglet.gl import *
except ImportError, e:
  print e
  sys.exit(1)

class Slideshow(pyglet.window.Window):
  "Controls the main window and its message loop."

  def __init__(self, fullscreen, width, height, visible=False, vsync=True):
    opts = {
      'visible': visible,
      'caption': 'Poseur',
      'fullscreen': fullscreen,
      'vsync': vsync,
    }

    if not fullscreen:
      opts['width'] = width
      opts['height'] = height

    pyglet.window.Window.__init__(self, **opts)

    self.rot = 0.0
    self.size = max(*self.get_size())
    self.x = self.get_size()[0]
    self.y = self.get_size()[1]

    self.curslide = 0

    # allow time to init window before displaying,
    # to avoid annoying white-out before going black

    self.set_visible()

    pyglet.clock.schedule(self.update)
    self.elapsed = 0.0

  def update(self, dt):
    "Called once for each frame, advances animation, etc."
    self.rot += 0.15
    if self.rot >= 360:
      self.rot -= 360
    self.elapsed += dt

    if options['verbose'] and self.elapsed >= 3.0:
      # display fps every 3 secs
      self.elapsed -= 3.0
      print "FPS is %f" % pyglet.clock.get_fps()

  def on_next_slide_step(self):
    "Called to increment slide step (mouseclick, space, etc)"
    if self.curslide+1 == len(slides):
      self.on_slideshow_end()
    else:
      self.curslide += 1

  def on_slideshow_end(self):
    "Called when reached end of slide show"
    sys.exit(0)

  def on_mouse_release(self, x, y, button, modifiers):
    self.on_next_slide_step()

  def on_draw(self):
    "Draw current slide"
    fontSize = self.size / 32.0

    text = pyglet.text.Label(slides[self.curslide],
      font_name='Helvetica',
      font_size=fontSize,
      color=(255,255,255,255))

    textHeight = fontSize

    self.clear()
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(0.0, self.y - textHeight, 0.0)
    text.draw()
    glPopMatrix()


def usage():
  print "Usage: poseur [ option(s) ]"
  print "Options:"
  print "  -h  --help        Show help"
  print "  -f  --fullscreen  View slideshow in fullscreen"
  print "  -v  --verbose     Print extra information to console"
  print "  -V  --version     Print version and exit"
  print "  -H  --height      Set screen height"
  print "  -W  --width       Set screen width"

def parse_opts(argv):
  try:
    opts, args = getopt.getopt(
      argv[1:],
      "hfvVW:H:",
      ["help", "fullscreen", "verbose", "version", "height=", "width="])

    for o, a in opts:
      if o in ("-h", "--help"):
        usage()
        sys.exit(0)
      elif o in ("-f", "--fullscreen"):
        options['fullscreen'] = True
      elif o in ("-v", "--verbose"):
        options['verbose'] = True
      elif o in ("-W", "--width"):
        options['width'] = int(a)
      elif o in ("-H", "--height"):
        options['height'] = int(a)
      elif o in ("-V", "--version"):
        print version
        print copyright
        print license
        sys.exit(0)

  except getopt.GetoptError, e:
    print "Error:", e
    print ""
    usage()
    sys.exit(2)

# don't run anything if we're invoked as "import poseur":
if __name__ == "__main__":
  parse_opts(sys.argv)
  window = Slideshow(
    fullscreen = options['fullscreen'],
    width      = options['width'],
    height     = options['height'])
  pyglet.app.run()
