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

version = '0.0.1'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'

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
    pyglet.window.Window.__init__(self,
      caption='Poseur',
      visible=visible,
      vsync=vsync,
      width=width,
      height=height,
      fullscreen=fullscreen)

    self.x = options['width']
    self.y = options['height']
    self.rot = 0.0
    self.size = max(self.x, self.y)

    self.label = pyglet.text.Label('Hello!',
      font_name='Helvetica',
      font_size=self.size / 16.0,
      x=0, #self.width//2,
      y=0, #self.height//2,
      anchor_x='center',
      anchor_y='center')

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

  def on_draw(self):
    "Called when screen must be redrawed"
    self.clear()
    glPushMatrix()

    glLoadIdentity()
    glTranslatef(self.x/2, self.y/2, 0.0)
    glRotatef(self.rot, 0, 0, 1)
    glScalef(self.size, self.size, 1.0)

    glBegin(GL_TRIANGLES)
    glColor4f(1.0, 0.0, 0.0, 0.0)
    glVertex2f(0.0, 0.5)
    glColor4f(0.0, 0.0, 1.0, 1.0)
    glVertex2f(0.2, -0.5)
    glColor4f(0.0, 0.0, 1.0, 1.0)
    glVertex2f(-0.2, -0.5)
    glEnd()

    glPopMatrix()

    glLoadIdentity()
    glTranslatef(self.x/2, self.y/2, 0.0)
    glScalef(2.0+math.cos(math.pi*2*self.rot/360.0), 2.0+math.cos(math.pi*2*self.rot/360.0), 1.0)
    glRotatef(-self.rot, 0, 0, 1)
    self.label.draw()

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
    opts, args = getopt.getopt(argv[1:], "hfvVW:H:",
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
