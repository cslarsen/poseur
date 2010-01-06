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
import pyglet
from pyglet.gl import *
from pyglet.window.key import *

version   = '0.0.3'
copyright = 'Copyright (C) 2010 Christian Stigen Larsen'
license   = 'Distributed under the (modified) BSD license'

# Browser keys on my particular computer (portable?)
USER_KEY_BACK    = 712964571136
USER_KEY_FORWARD = 717259538432

GRAD_COL_TOP = (0.6, 0.6, 0.6)
GRAD_COL_BOTTOM = (1.0, 1.0, 1.0)

# The slideshow to present
slides = []

def parseOptions(argv):
  "Set program options and return files to process."
  p = optparse.OptionParser()

  p.add_option("-f", "--fullscreen", dest="FULLSCREEN",
               action="store_true", default=False,
               help="View presentation in fullscreen")

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

  p.add_option("-F", "--font", dest="NORMAL_FONT",
               metavar="NAME", default='Helvetica',
               help="Set font name (default: %default)")

  p.add_option("-C", "--fixed-font", dest="FIXED_WIDTH_FONT",
               metavar="NAME", default='Courier New',
               help="Set fixed width font name (default: %default)")

  global option
  (option, files) = p.parse_args()

  if option.VERSION:
    print "poseur", version
    print copyright
    print license
    print ""
    print "Using pyglet version", pyglet.version
    print ""
    print "OpenGL version:", gl_info.get_version()
    print "OpenGL vendor:", gl_info.get_vendor()
    print "OpenGL renderer:", gl_info.get_renderer()
    sys.exit(0)

  return files

def verbose(s):
  "Print message if verbose option is set"
  if option.VERBOSE:
    print s

def makeText(text, width, font_name=None, font_size=12, color = (0,0,0,255)):
    r = pyglet.text.HTMLLabel(text=text, width=width, multiline=True)

    if font_name == None:
      font_name = option.NORMAL_FONT

    r.font_name = font_name
    r.font_size = font_size
    r.color     = color

    if re.match("<pre>", text):
      r.font_name = option.FIXED_WIDTH_FONT

    return r

class Slideshow(pyglet.window.Window):
  "Controls the main window and its message loop."

  def addText(self, text):
    self.items.append(makeText(
        text      = text,
        width     = self.x - (self.size / 64.0),
        font_size = self.size / 32.0))

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

    self.curslide = 0
    self.curitem = 0

    # allow time to init window before displaying,
    # to avoid annoying white-out before going black
    pyglet.clock.schedule_once(self.setVisible, 0.01)

    pyglet.clock.schedule(self.update)
    self.elapsed = 0.0
    self.elapsedHideMouse = 0.0

    self.setupGL()

    # add first text item
    self.items = []
    self.addText(slides[self.curslide][self.curitem])

  def setupGL(self):
    glEnable(GL_BLEND)
    glShadeModel(GL_SMOOTH)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);

  def setVisible(self, foo):
    self.set_visible()

    if option.FULLSCREEN:
      self.hideMouse()

  def hideMouse(self):
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

  def nextSlide(self):
    self.curslide += 1

    if self.curslide < len(slides):
      self.items   = []
      self.curitem = -1
      self.nextItem()
    else:
      self.on_slideshow_end()

  def nextItem(self):
    self.curitem += 1

    if self.curitem < len(slides[self.curslide]):
      self.addText(slides[self.curslide][self.curitem])
    else:
      self.nextSlide()

  def on_next_slide_step(self):
    self.nextItem()

  def on_prev_slide_step(self):
    "Go backwards one step in slideshow"
    if self.curitem == 0:
      if self.curslide > 0:
        # previous slide
        self.curslide -= 1
        self.curitem = len(slides[self.curslide]) - 1

        # add all items
        self.items = []
        [self.addText(x) for x in slides[self.curslide]]
    else:
      self.curitem -= 1
      self.items = self.items[:-1] # pop last item

  def on_slideshow_end(self):
    "Called when reached end of slide show"
    pass

  def on_mouse_motion(self, x, y, dx, dy):
    self.showMouse()
    self.elapsedHideMouse = 0.0

  def on_mouse_release(self, x, y, button, modifiers):
    if button == 1: # left button?
      self.on_next_slide_step()

  def on_key_release(self, symbol, modifiers):
    if symbol in (RIGHT, SPACE, ENTER, USER_KEY_FORWARD):
      self.on_next_slide_step()
    elif symbol in (LEFT, BACKSPACE, USER_KEY_BACK):
      self.on_prev_slide_step()

  def on_draw(self):
    "Draw current slide"

    self.clear()

    glPushMatrix()
    glLoadIdentity()
    glTranslatef(self.x/2, self.y/2, 0.0)
    glBegin(GL_QUADS)
    glColor3f(*GRAD_COL_BOTTOM)
    glVertex2f(-self.x, -self.y + (self.y/2))
    glVertex2f(self.x, -self.y + (self.y/2));
    glColor3f(*GRAD_COL_TOP)
    glVertex2f(self.x, self.y - (self.y/2));
    glVertex2f(-self.x, self.y - (self.y/2));
    glEnd()
    glPopMatrix()
 
    # initial position
    glLoadIdentity()
    glTranslatef(self.size/64.0, self.y-(self.size/32.0)-(self.size/64.0), 0.0)

    for item in self.items[:-1]:
      item.draw()
      glTranslatef(0, -item.content_height, 0.0) # move down

    # draw last one as well
    if len(self.items) > 0:
      self.items[-1].draw()

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
      slide.append(expandUnicode(line))
      newline = False
    else:
      if newline:
        slides += [slide]
        slide = []
        newline = False
      else:
        if len(slide) > 0:
          slide[-1] += '<br />'
        newline = True

  if len(slide) > 0:
    slides += [slide]

  return slides

if __name__ == "__main__":
  try:
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

  except KeyboardInterrupt, e:
    sys.exit(0)
