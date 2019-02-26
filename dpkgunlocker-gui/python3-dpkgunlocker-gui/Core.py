#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import os
import sys
import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager

from . import MainWindow
from . import ProcessBox
from . import settings

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class Core:
	
	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/dpkgunlocker.ui"
		self.unlockerManager=DpkgUnlockerManager.DpkgUnlockerManager()
		self.isDpkgUnlocker_running()
		self.check_root()
		
		self.processBox=ProcessBox.ProcessBox()
			
			
		self.mainWindow=MainWindow.MainWindow()
			
		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	def isDpkgUnlocker_running(self):

		if os.path.exists('/var/run/dpkgUnlocker.lock'):
			print ("  [Dpkg-Unlocker-Gui]: Dpkg-Unlocker is now running ")
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Dpkg-Unlocker")
			dialog.format_secondary_text(_("Dpkg-Unlocker is now running. Wait a moment and try again."))
			dialog.run()
			sys.exit(1)
		else:
			self.unlockerManager.createLockToken()		

	def check_root(self):
		
		try:
			print("  [Dpkg-Unlocker-Gui]: Checking root")
			f=open("/var/run/DpkgUnlocker.token","w")
			f.close()
			os.remove("/var/run/DpkgUnlocker.token")
		except:
			print("  [Dpkg-Unlocker-Gui]: No administration privileges")
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Dpkg-Unlocker")
			dialog.format_secondary_text(_("You need administration privileges to run this application."))
			dialog.run()
			sys.exit(1)
		
	#def check_root
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
