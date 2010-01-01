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

  def __init__(self, visible=False, vsync=True, fullscreen=False):
    pyglet.window.Window.__init__(self,
      caption='Poseur',
      visible=visible,
      vsync=vsync,
      width=options['width'],
      height=options['height'],
      fullscreen=fullscreen)

    self.label = pyglet.text.Label('Hello!',
      font_name='Helvetica',
      font_size=97,
      x=0, #self.width//2,
      y=0, #self.height//2,
      anchor_x='center',
      anchor_y='center')

    # allow time to init window before displaying,
    # to avoid annoying white-out before going black

    self.set_visible()
    self.x = options['width']
    self.y = options['height']
    self.rot = 0.0
    self.size = 300.0

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
    glTranslatef(self.x, self.y, 0.0)
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
    glTranslatef(self.x, self.y, 0.0)
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

def parse_opts(argv):
  try:
    opts, args = getopt.getopt(argv[1:], "hfvV",
      ["help", "fullscreen", "verbose", "version"])
    for o, a in opts:
      if o in ("-h", "--help"):
        usage()
        sys.exit()
      elif o in ("f", "--fullscreen"):
        options['fullscreen'] = True
      elif o in ("v", "--verbose"):
        options['verbose'] = True
      elif o in ("V", "--version"):
        print version
        print copyright
        sys.exit()

  except getopt.GetoptError, e:
    print "Error:", e
    print ""
    usage()
    sys.exit(2)

# don't run anything if we're invoked as "import poseur":
if __name__ == "__main__":
  parse_opts(sys.argv)
  window = Slideshow(fullscreen=options['fullscreen'])
  pyglet.app.run()
