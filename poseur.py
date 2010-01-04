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
import re
import optparse

# Program options
option = {}

# Program strings
version   = '0.0.2'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'
license   = 'Distributed under the (modified) BSD license'

# Browser keys on my particular computer
# Is this portable across Windows installations?
USER_KEY_BACK    = 712964571136
USER_KEY_FORWARD = 717259538432

# The slideshow to present
slides = []

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
    print "Program arguments:", files
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

class Item:
  "An item on screen"
  def __init__(self):
    pass

  def on_enter(self):
    "Signal start of enter animation"
    pass

  def on_exit(self):
    "Signal start of exit animation"
    pass

  def is_anim_finished(self):
    "True if enter/exit animation has ended"
    return True

  def on_draw(self):
    "Draw the object on screen"
    pass

  def bounds(self):
    "Return bounding box dimension (width, height)"
    return (0, 0)

class TextItem(Item):
  def __init__(self, text, useHTML, width, fontName = 'Helvetica', fontSize = 12, color = (0, 0, 0, 255)):
    if useHTML:
      self.label = pyglet.text.HTMLLabel()
    else:
      self.label = pyglet.text.Label()

    self.label.text      = text
    self.label.width     = width
    self.label.multiline = True
    self.label.font_name = fontName
    self.label.font_size = fontSize
    self.label.color     = color

  def on_draw(self):
    self.label.draw()

  def bounds(self):
    return (self.label.content_width, self.label.content_height)

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
    self.curitem = 0

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
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
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

    if (self.curitem + 1) == len(slides[self.curslide]):
      if (self.curslide + 1) == len(slides):
        self.on_slideshow_end()
      else:
        debug("Go forward slide (curslide=%d, curitem=%d)" % (self.curslide, self.curitem))
        self.curitem = 0
        self.curslide += 1
    else:
      debug("Go forward item (curslide=%d, curitem=%d)" % (self.curslide, self.curitem))
      self.curitem += 1

  def on_prev_slide_step(self):
    "Go backwards one step in slideshow"
    if self.curitem == 0:
      if self.curslide > 0:
        debug("Go backwards")
        self.curslide -= 1
        self.curitem = len(slides[self.curslide]) - 1
    else:
      self.curitem -= 1

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

    self.clear()

    glPushMatrix()
   
    glLoadIdentity()
    glTranslatef(self.x/2, self.y/2, 0.0)
 
    white = (1.0, 1.0, 1.0)
    gray = (0.6, 0.6, 0.6)

    glBegin(GL_QUADS)
    glColor3f(*white)
    glVertex2f(-self.x, -self.y + (self.y/2))
    glVertex2f(self.x, -self.y + (self.y/2));
    glColor3f(*gray)
    glVertex2f(self.x, self.y - (self.y/2));
    glVertex2f(-self.x, self.y - (self.y/2));
    glEnd()
 
    glPopMatrix()
 
    glLoadIdentity()

    # initial position
    glTranslatef(self.size / 64.0, self.y - (self.size/32.0) - (self.size / 64.0), 0.0)

    for item in slides[self.curslide][:(1+self.curitem)]:
      label = TextItem(
        text     = item,
        width    = self.x - (self.size / 64.0),
        useHTML  = True,
        fontSize = self.size / 32.0)

      label.on_draw()

      # move down to next line after drawing
      glTranslatef(0, -label.bounds()[1], 0.0)

def parseLine(line):
  if re.match("^ {2,}", line):
    return "<PRE>" + line.strip() + "</PRE>"

  # ORDER DEPENDENCY
  line = re.sub("\/([^\/]+)\/", "<i>\\1</i>", line)
  line = re.sub("\*([^\*]+)\*", "<b>\\1</b>", line)
  line = re.sub("\_([^\_]+)\_", "<u>\\1</u>", line)

  if re.match("^ *[-\*] ", line):
    return "<ul><li>" + re.sub("^ *[-\*]", "", line) + "</li></ul>"

  return line

def expandUnicode(line):
  s = ""
  for c in line:
    if ord(c) > 127:
      s += "&#%d;" % ord(c)
    else:
      s += c
  return s

def readSlides(lines):
  "Parse slideshow."

  slides = []
  slide = []

  newline = False

  for line in lines:
    if len(line.strip()) > 0:
      slide.append(expandUnicode(parseLine(line)))
      newline = False
    else:
      if newline:
        slides += [slide]
        slide = []
        newline = False
      else:
        slide[-1] += '<br />'
        newline = True

  if len(slide) > 0:
    slides += [slide]

  return slides

if __name__ == "__main__":

  files = parseOptions(sys.argv)

  if files:
    for file in files:
      f = open(file, "rt")
      slides += readSlides(f.readlines())
      f.close()
  else:
    slides = readSlides(sys.stdin.readlines())

  window = Slideshow(
    fullscreen = option.FULLSCREEN,
    width      = option.WIDTH,
    height     = option.HEIGHT)

  pyglet.app.run()
