#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Poseur is a simple presentation viewer.

Copyright (C) 2010 Christian Stigen Larsen
Distributed under the (modified) BSD license.

http://github.com/cslarsen/poseur
"""

# the red book online: http://fly.cc.fer.hr/~unreal/theredbook/

import sys
import math
import optparse

# Program options
option = {}

# Program strings
version   = '0.0.1'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'
license   = 'Distributed under the (modified) BSD license'

# Browser keys on my particular computer
# Is this portable across Windows installations?
USER_KEY_BACK    = 712964571136
USER_KEY_FORWARD = 717259538432

# The slideshow to present
slides = [
  'What is Poseur?',
  'What is Poseur?<br/><br/>- A <i>simple</i> presentation viewer',
  'What is Poseur?<br/><br/>- A <i>simple</i> presentation viewer<br/>- Written in <b>Python</b>',
  'What is Poseur?<br/><br/>- A <i>simple</i> presentation viewer<br/>- Written in <b>Python</b><br/>- Free and open source',
]

try:
  import pyglet
  from pyglet.gl import *
except ImportError, e:
  print e
  sys.exit(1)

def parseOptions(argv):
  "Set program options and return files to process."
  p = optparse.OptionParser()

  p.add_option("-f", "--fullscreen", dest="FULLSCREEN",
               action="store_true", default=False,
               help="View presentation in fullscreen")

  p.add_option("-d", "--debug", dest="DEBUG",
               action="store_true", default=False,
               help="Print debugging information to console")

  p.add_option("-v", "--verbose", dest="VERBOSE",
               action="store_true", default=False,
               help="Print extra information to console")

  p.add_option("-V", "--version", dest="VERSION",
               action="store_true", default=False,
               help="Print program version and exit")

  p.add_option("-W", "--width", dest="WIDTH",
               type="int", default=640,
               help="Set window width (default: %default)")

  p.add_option("-H", "--height", dest="HEIGHT",
               type="int", default=480,
               help="Set window height (default: %default)")

  global option
  (option, files) = p.parse_args()

  if option.DEBUG:
    print "Poseur options:", option
    print "Program argumentseurArguments:", files
    print ""
    print "Pyglet options:", pyglet.options
    print ""

  if option.VERSION:
    print "poseur", version
    print copyright
    print license
    print ""
    print "Using pyglet version", pyglet.version
    print ""
    print "OpenGL version:", pyglet.gl.gl_info.get_version()
    print "OpenGL vendor:", pyglet.gl.gl_info.get_vendor()
    print "OpenGL renderer:", pyglet.gl.gl_info.get_renderer()
    sys.exit(0)

  return files

def verbose(s):
  "Print message if verbose option is set"
  if option.VERBOSE:
    print s

def debug(s):
  "Print message if debug option is set"
  if option.DEBUG:
    print s

class Slideshow(pyglet.window.Window):
  "Controls the main window and its message loop."

  def __init__(self, fullscreen, width, height, visible=False, vsync=True):

    pygOpts = {
      'visible':    visible,
      'caption':    'Poseur',
      'fullscreen': fullscreen,
      'vsync':      vsync,
    }

    # Pyglet only accepts dimensions in
    # windowed mode
    if not fullscreen:
      pygOpts['width']  = width
      pygOpts['height'] = height

    pyglet.window.Window.__init__(self, **pygOpts)

    self.x, self.y = self.get_size()
    self.size = math.sqrt(self.x ** 2 + self.y ** 2)
    debug("Screen dimensions: %dx%d pixels" % (self.x, self.y))

    self.curslide = 0

    # allow time to init window before displaying,
    # to avoid annoying white-out before going black
    pyglet.clock.schedule_once(self.setVisible, 0.01)

    pyglet.clock.schedule(self.update)
    self.elapsed = 0.0
    self.elapsedHideMouse = 0.0

    self.setupGL()

  def setupGL(self):
    glEnable(GL_BLEND)
    glShadeModel(GL_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST);
    glDisable(GL_DEPTH_TEST)

  def setVisible(self, foo):
    debug("Set visible")
    self.set_visible()

    if option.FULLSCREEN:
      self.hideMouse()

  def hideMouse(self):
    debug("Hiding mouse")
    self.set_exclusive_mouse(True)

  def showMouse(self):
    self.set_exclusive_mouse(False)

  def update(self, dt):
    "Called once for each frame, advances animation, etc."
    self.elapsed += dt
    self.elapsedHideMouse += dt

    if self.elapsed >= 3.0:
      self.elapsed -= 3.0
      verbose("FPS is %f" % pyglet.clock.get_fps())

    # hide mouse after a while
    if self.elapsedHideMouse >= 3.0:
      self.elapsedHideMouse -= 3.0
      if option.FULLSCREEN:
        self.hideMouse()

  def on_next_slide_step(self):
    "Go forward one step in slideshow"
    if (self.curslide + 1) == len(slides):
      self.on_slideshow_end()
    else:
      debug("Go forward")
      self.curslide += 1

  def on_prev_slide_step(self):
    "Go backwards one step in slideshow"
    if self.curslide > 0:
      debug("Go backwards")
      self.curslide -= 1

  def on_slideshow_end(self):
    "Called when reached end of slide show"
    debug("Slide show ended")

  def on_mouse_motion(self, x, y, dx, dy):
    # show mouse again
    self.showMouse()
    self.elapsedHideMouse = 0.0

  def on_mouse_release(self, x, y, button, modifiers):
    debug("Mouse button released: x=%d y=%d button=%s modifiers=%s" % (
      x, y, button, modifiers))

    # advance on left button press
    if button & 0x1: # is it really bitmasked?
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
    paddingPx = fontSize / 2.0

    useHTML = True

    if useHTML:
      text = pyglet.text.HTMLLabel()
    else:
      text = pyglet.text.Label()

    text.text = slides[self.curslide]
    text.width = self.x - paddingPx
    text.multiline = True
    text.font_name = 'Helvetica'
    text.font_size = fontSize
    text.color = (0, 0, 0, 255)

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

if __name__ == "__main__":

  files = parseOptions(sys.argv)

  window = Slideshow(
    fullscreen = option.FULLSCREEN,
    width      = option.WIDTH,
    height     = option.HEIGHT)

  pyglet.app.run()
