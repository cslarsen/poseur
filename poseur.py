#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Poseur is a simple presentation viewer.

Copyright (C) 2010 Christian Stigen Larsen
Distributed under the (modified) BSD license.

http://github.com/cslarsen/poseur
"""

# the red book online: http://fly.cc.fer.hr/~unreal/theredbook/

import sys
import getopt
import math

version   = '0.0.1'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'
license   = 'Distributed under the (modified) BSD license'

# browser keys on my particular computer, it this (semi) portable?
USER_KEY_BACK = 712964571136
USER_KEY_FORWARD = 717259538432

slides = [
  'What is Poseur?',
  '- A simple presentation software',
  '- Written in Python',
  '- Free and open source',
]

endSlide = '' # "(End of slideshow)"

options = {
  'fullscreen': False,
  'verbose':    False,
  'debug':      False,
  'width':       1024,
  'height':       768,
}

try:
  import pyglet
  from pyglet.gl import *
except ImportError, e:
  print e
  sys.exit(1)

def verbose(s):
  "Print message if verbose option is set"
  if options['verbose']: print s

def debug(s):
  "Print message if debug option is set"
  if options['debug']: print s

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
    debug("Screen dimensions are %dx%d pixels" % (self.x, self.y))

    self.curslide = 0

    # allow time to init window before displaying,
    # to avoid annoying white-out before going black

    self.set_visible()

    # at startup, insert the END OF SLIDESHOW slide
    slides.append(endSlide)

    pyglet.clock.schedule(self.update)
    self.elapsed = 0.0

  def update(self, dt):
    "Called once for each frame, advances animation, etc."
    self.rot += 0.15
    if self.rot >= 360:
      self.rot -= 360
    self.elapsed += dt

    if options['verbose'] and self.elapsed >= 3.0:
      self.elapsed -= 3.0
      verbose("FPS is %f" % pyglet.clock.get_fps())

  def on_next_slide_step(self):
    "Go forward one step in slideshow"
    if self.curslide+1 == len(slides):
      self.on_slideshow_end()
    else:
      self.curslide += 1

  def on_prev_slide_step(self):
    "Go backwards one step in slideshow"
    if self.curslide > 0:
      self.curslide -= 1

  def on_slideshow_end(self):
    "Called when reached end of slide show"
    pass

  def on_mouse_release(self, x, y, button, modifiers):
    debug("Mouse button released: x=%d y=%d button=%s modifiers=%s" % (
      x, y, button, modifiers))

    self.on_next_slide_step()

  def on_key_release(self, symbol, modifiers):
    debug("Key released: %s (%d)" % (
      pyglet.window.key.symbol_string(symbol),
      symbol))

    if symbol in (pyglet.window.key.RIGHT,
                  pyglet.window.key.SPACE,
                  pyglet.window.key.ENTER,
                  USER_KEY_FORWARD):
      self.on_next_slide_step()

    elif symbol in (pyglet.window.key.LEFT,
                    pyglet.window.key.BACKSPACE,
                    USER_KEY_BACK):
      self.on_prev_slide_step()

  def on_draw(self):
    "Draw current slide"
    fontSize = self.size / 32.0
    paddingPx = 10

    text = pyglet.text.Label(slides[self.curslide],
      font_name='Helvetica',
      font_size=fontSize,
      color=(0, 0, 0, 255))

    textHeight = fontSize

    self.clear()

    glPushMatrix()
 
    glLoadIdentity()
    glTranslatef(self.x/2, self.y/2, 0.0)
 
    glBegin(GL_QUADS)
    glColor3f(1.0,1.0,1.0) # white
    glVertex2f(-self.x, -self.y + (self.y/2))
    glVertex2f(self.x, -self.y + (self.y/2));
    glColor3f(0.6,0.6,0.6) # gray
    glVertex2f(self.x, self.y - (self.y/2));
    glVertex2f(-self.x, self.y - (self.y/2));
    glEnd()
 
    glPopMatrix()
 
    glLoadIdentity()
    glTranslatef(paddingPx, self.y - fontSize - paddingPx, 0.0)
    text.draw()

def usage():
  print "Usage: poseur [ option(s) ]"
  print "Options:"
  print "  -h  --help        Show help"
  print "  -d  --deubg       Print extra debugging information to console"
  print "  -f  --fullscreen  View slideshow in fullscreen"
  print "  -v  --verbose     Print extra information to console"
  print "  -V  --version     Print version and exit"
  print "  -H  --height      Set screen height"
  print "  -W  --width       Set screen width"

def parse_opts(argv):
  try:
    opts, args = getopt.getopt(
      argv[1:],
      "hfvVW:H:d",
      ["help", "fullscreen", "verbose", "version", "height=", "width=", "debug"])

    for o, a in opts:
      if o in ("-h", "--help"):
        usage()
        sys.exit(0)
      elif o in ("-f", "--fullscreen"):
        options['fullscreen'] = True
      elif o in ("-d", "--debug"):
        options['debug'] = True
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
