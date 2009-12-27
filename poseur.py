#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyglet
from pyglet.gl import *

class Slideshow(pyglet.window.Window):
	def __init__(self):
		pyglet.window.Window.__init__(self,
			caption='Poseur',
			visible=False,
			vsync=True,
			fullscreen=False)

		self.label = pyglet.text.Label('Hello!',
			font_name='Times New Roman',
			font_size=36,
			x=self.width//2,
			y=self.height//2,
			anchor_x='center',
			anchor_y='center')

		# allow time to init window before displaying,
		# to avoid annoying white-out before going black

		self.set_visible()
		self.x = 320
		self.y = 240
		self.rot = 0.4
		self.size = 300.0

	def on_draw(self):
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
		self.rot = self.rot + 1.1
		self.label.draw()

if __name__ == "__main__":
	window = Slideshow()
	pyglet.app.run()
