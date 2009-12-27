#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore, QtOpenGL

#try:
#	from OpenGL import GL
#except ImportError:
#	app = QtGui.QApplication(sys.argv)
#	print("PyOpenGL must be installed")
	#sys.exit(1)

def init():
	"Set up graphical environment"
	pass

def read(fp):
	"Read presentation from file"
	return {'slide': {'text': 'Hello'}}

def log(str):
	print(str)

def show(pres):
	"Show presentation"
	pass

class Wiggy(QtOpenGL.QGLWidget):
	def __init__(self, parent):
		QtOpenGL.QGLWidget.__init__(self, parent)
		self.setMinimumSize(500, 500)

class Test(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		w = Wiggy(self)
		self.setCentralWidget(w)

a = QtGui.QApplication(sys.argv)
w = Test()
w.show()
a.exec_()
