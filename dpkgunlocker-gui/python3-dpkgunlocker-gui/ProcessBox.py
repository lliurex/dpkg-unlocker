#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Vte

import copy

import sys
import os



from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class ProcessBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"dpkgunlocker-gui.css"

		self.padlock_closed=self.core.rsrc_dir+"padlock_closed.svg"
		self.padlock_open=self.core.rsrc_dir+"padlock_open.svg"
		self.ok_img=self.core.rsrc_dir+"ok.svg"
		self.error_img=self.core.rsrc_dir+"error.svg"
		

		self.main_box=builder.get_object("process_data_box")
		self.process_list_box=builder.get_object("process_box_list")
		
		self.llxup_padlock=builder.get_object("llxup_padlock")
		self.llxup_name_label=builder.get_object("llxup_name_label")
		self.llxup_status_label=builder.get_object("llxup_status_label")
		self.llxup_status_img=builder.get_object("llxup_status_img")
		self.llxup_status_img.set_size_request(24,24)


		self.dpkg_padlock=builder.get_object("dpkg_padlock")
		self.dpkg_name_label=builder.get_object("dpkg_name_label")
		self.dpkg_status_label=builder.get_object("dpkg_status_label")
		self.dpkg_status_img=builder.get_object("dpkg_status_img")
		self.dpkg_status_img.set_size_request(24,24)


		self.apt_padlock=builder.get_object("apt_padlock")
		self.apt_name_label=builder.get_object("apt_name_label")
		self.apt_status_label=builder.get_object("apt_status_label")
		self.apt_status_img=builder.get_object("apt_status_img")
		self.apt_status_img.set_size_request(24,24)


		self.terminal_box=builder.get_object("terminal_box")
		self.terminal_config=self.core.rsrc_dir+"terminal.conf"
		self.feedback_msg_box=builder.get_object("feedback_msg_box")
		self.feedback_ok_img=builder.get_object("feedback_ok_img")
		self.feedback_error_img=builder.get_object("feedback_error_img")
		self.feedback_information_img=builder.get_object("feedback_information_img")

		self.terminal_label=builder.get_object("terminal_label")
		self.terminal_viewport=builder.get_object("viewport")
		self.terminal_scrolled=builder.get_object("terminalScrolledWindow")
		self.vterminal=Vte.Terminal()
		self.vterminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			["/bin/bash","--rcfile",self.terminal_config],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
		)
		font_terminal = Pango.FontDescription("monospace normal 9")
		self.vterminal.set_font(font_terminal)
		self.vterminal.set_scrollback_lines(-1)
		self.vterminal.set_sensitive(True)
		self.terminal_scrolled.add(self.vterminal)
		
		self.pack_start(self.main_box,True,True,0)
		
		self.set_css_info()
		
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
	
		self.llxup_name_label.set_name("PROCESS_NAME")
		self.dpkg_name_label.set_name("PROCESS_NAME")
		self.apt_name_label.set_name("PROCESS_NAME")
		self.process_list_box.set_name("WINDOW")

	#def set_css_info			
			
	def load_info(self,info,log):

		self.llxup_padlock.set_from_file(self.get_padlock_img(info["Lliurex-Up"]))
		self.llxup_status_label.set_text(self.get_status_msg(info["Lliurex-Up"]))
		self.llxup_status_img.set_from_file(self.get_status_img(info["Lliurex-Up"]))
		self.set_status_css(info["Lliurex-Up"],"Lliurex-Up")

		self.dpkg_padlock.set_from_file(self.get_padlock_img(info["Dpkg"]))
		self.dpkg_status_label.set_text(self.get_status_msg(info["Dpkg"]))
		self.dpkg_status_img.set_from_file(self.get_status_img(info["Dpkg"]))
		self.set_status_css(info["Dpkg"],"Dpkg")

		self.apt_padlock.set_from_file(self.get_padlock_img(info["Apt"]))
		self.apt_status_label.set_text(self.get_status_msg(info["Apt"]))
		self.apt_status_img.set_from_file(self.get_status_img(info["Apt"]))
		self.set_status_css(info["Apt"],"Apt")

		if log:
			self.core.mainWindow.write_log("Dpkg-Unlocker-gui")
			self.write_status_log(info["Lliurex-Up"],"Lliurex-Up")
			self.write_status_log(info["Dpkg"],"Dpkg")
			self.write_status_log(info["Apt"],"Apt")

		
	#def load_info				

	def get_status_msg(self,code):

		if code==0:
			msg=_("Unlocked")
		elif code==1:
			msg=_("Locked: Currently executing")
		elif code==2:		
			msg=_("Locked: Not process found")
		elif code==3:
			msg=_("Locked: Apt currently executing")
		elif code==4:
			msg=_("Locked: Apt daemon currently executing")
	

		return msg	


	#def get_status_msg	

	def set_status_css(self,code,process):

		if code==2:
			if process=="Lliurex-Up":
				self.llxup_status_label.set_name("PROCESS_STATUS_ERROR")
			elif process=="Dpkg":
				self.dpkg_status_label.set_name("PROCESS_STATUS_ERROR")
			elif process=="Apt":	
				self.apt_status_label.set_name("PROCESS_STATUS_ERROR")
		else:
			if process=="Lliurex-Up":
				self.llxup_status_label.set_name("PROCESS_STATUS")
			elif process=="Dpkg":
				self.dpkg_status_label.set_name("PROCESS_STATUS")
			elif process=="Apt":	
				self.apt_status_label.set_name("PROCESS_STATUS")	

	#def set_status_css				

	def get_padlock_img(self,code):

		if code==0:
			img=self.padlock_open
		else:
			img=self.padlock_closed

		return img	

	#def get_padklock_img

	def get_status_img(self,code):
	
		if code!=2:
			img=self.ok_img
		else:
			img=self.error_img

		return img	

	#def get_status_img								

	def write_status_log(self,code,process):

		if code==0:
			if process=="Lliurex-Up":
				msg="Lliurex-Up: Unlocked"
			elif process=="Dpkg":
				msg="Dpkg: Unlocked"
			elif process=="Apt":	
				msg="Apt: Unlocked"

		elif code==1:
			if process=="Lliurex-Up":
				msg="Lliurex-Up: Locked. Currently executing"
			elif process=="Dpkg":
				msg="Dpkg: Locked. Currently executing"
			elif process=="Apt":	
				msg="Apt: Locked. Currently executing"		

		elif code==2:
			if process=="Lliurex-Up":
				msg="Lliurex-Up: Locked. Not process found"
			elif process=="Dpkg":
				msg="Dpkg: Locked. Not process found"
			elif process=="Apt":	
				msg="Apt: Locked. Not process found"

		elif code==3:
			msg="Dpkg: Locked. Apt currently executing "
			
		elif code==4:
			if process=="Dpkg":
				msg="Dpkg: Locked. Apt daemon executing"
			elif process=="Apt":
				msg="Apt: Locked. Apt daemon executing"
		

		self.core.mainWindow.write_log(msg)


	#def write_status_log					

	def manage_vterminal(self,enabled_input,sensitive):

		self.vterminal.set_input_enabled(enabled_input)
		self.vterminal.set_sensitive(sensitive)	

	#def manage_vterminal

	def manage_feedback_box(self,hide,error,info=False):

		if hide:
			self.feedback_msg_box.set_name("HIDE_BOX")
			self.feedback_ok_img.hide()
			self.feedback_error_img.hide()
			self.feedback_information_img.hide()
		else:
			self.terminal_label.set_name("FEEDBACK_LABEL")
			self.terminal_label.set_halign(Gtk.Align.START)

			if error:
				self.feedback_msg_box.set_name("ERROR_BOX")
				self.feedback_ok_img.hide()
				self.feedback_error_img.show()
				self.feedback_information_img.hide()
			else:
				if not info:
					self.feedback_msg_box.set_name("SUCCESS_BOX")
					self.feedback_ok_img.show()
					self.feedback_error_img.hide()
					self.feedback_information_img.hide()
				else:
					self.feedback_msg_box.set_name("INFORMATION_BOX")
					self.feedback_ok_img.hide()
					self.feedback_error_img.hide()
					self.feedback_information_img.show()

	#def manage_feedback_box


#class ProcessBox

from . import Core