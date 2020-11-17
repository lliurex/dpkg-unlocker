#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib


import signal
import os
import subprocess
import json
import sys
import syslog
import time
import threading
import tempfile
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class MainWindow:
	
	def __init__(self):

		self.core=Core.Core.get_core()
	
	#def init
	
	
	def load_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		
		self.css_file=self.core.rsrc_dir+"dpkgunlocker-gui.css"

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(10)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("Dpkg-Unlocker")
		self.main_box=builder.get_object("main_box")
		self.main_window.resize(640,620)
		self.image_box=builder.get_object("image_box")
		self.help_button=builder.get_object("help_button")
		self.unlock_button=builder.get_object("unlock_button")

		self.process_box=self.core.processBox
		self.stack.add_titled(self.process_box,"processBox","ProcessBox")
		self.main_box.pack_start(self.stack,True,False,5)
		self.main_window.show_all()
		self.process_box.terminal_viewport.hide()
		
		self.final_column=0
		self.final_row=0

		self.set_css_info()
		self.init_threads()
		self.connect_signals()
		self.is_working=False
		self.load_info(True)
		GLib.timeout_add_seconds(5, self.is_worker)
		
	#def load_gui


	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		self.image_box.set_name("IMAGE_BOX")
		self.process_box.terminal_label.set_name("MSG_LABEL")
		

	#def set_css_info	
				

	def init_threads(self):

		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True

		GObject.threads_init()

	#def init_threads	


	def connect_signals(self):

		self.main_window.connect("destroy",self.quit)
		self.help_button.connect("clicked",self.help_clicked)
		self.unlock_button.connect("clicked",self.unlock_process)

	#def connect_signals	

	def is_worker(self):

		if not self.is_working:
			self.load_info(False)
					
		return True

	#def is_worker		

	def load_info(self,log):

		info=self.core.unlockerManager.checkingLocks()
		self.manage_unlock_button(info)
		self.process_box.load_info(info,log)

	#def load_info

	
	def manage_unlock_button(self,info):

		cont=0
		ok_status=[0,1,3,4]
		running_status=[1,3,4]
		liveProcess=0

		for item in info:
			if info[item] in ok_status:
				cont+=1
			if info [item] in running_status:
				liveProcess+=1	

		if cont==3:
			self.unlock_button.set_sensitive(False)
			self.process_box.terminal_label.set_text(self.get_msg_text(0))

		else:
			if cont==0:
				self.unlock_button.set_sensitive(True)
			else:
				if liveProcess>0:
					self.unlock_button.set_sensitive(False)
					self.process_box.terminal_label.set_text(self.get_msg_text(11))	
				else:
					self.unlock_button.set_sensitive(True)
					self.process_box.terminal_label.set_text(self.get_msg_text(12))	

	#def manage_unlock_button
	
	def init_unlocker_processes(self):

		self.remove_llxup_lock_launched=False
		self.remove_llxup_lock_done=False

		self.remove_dpkg_lock_launched=False
		self.remove_dpkg_lock_done=False

		self.remove_apt_lock_launched=False
		self.remove_apt_lock_done=False

		self.fixing_system_launched=False
		self.fixing_system_done=False

	#def init_unlocker_processes	

	def create_process_token(self,command,action):


		if action=="Lliurex-Up":
			self.token_llxup_process=tempfile.mkstemp('_LlxUp')
			remove_tmp=' rm -f ' + self.token_llxup_process[1] + ';'+'\n'
			
		elif action=="Dpkg":
			self.token_dpkg_process=tempfile.mkstemp('_Dpkg')
			remove_tmp=' rm -f ' + self.token_dpkg_process[1] + ';'+'\n'

		elif action=="Apt":
			self.token_apt_process=tempfile.mkstemp('_Apt')	
			remove_tmp=' rm -f ' + self.token_apt_process[1] + ';'+'\n'
			
		elif action=="Fixing":
			self.token_fixing_process=tempfile.mkstemp('_Fixing')	
			remove_tmp=' rm -f ' + self.token_fixing_process[1] + ';'+'\n'

		cmd=command+remove_tmp
		return cmd

	#def create_process_token	

	def create_result_token(self,command,action):


		if action=="Lliurex-Up":
			self.token_llxup_result=tempfile.mkstemp('_LlxUp')
			result_tmp=' echo $? >' + self.token_llxup_result[1]+ ';'
			
		elif action=="Dpkg":
			self.token_dpkg_result=tempfile.mkstemp('_Dpkg')
			result_tmp=' echo $? > ' + self.token_dpkg_result[1] + ';'

		elif action=="Apt":
			self.token_apt_result=tempfile.mkstemp('_Apt')	
			result_tmp=' echo $? > ' + self.token_apt_result[1] + ';'
			
		elif action=="Fixing":
			self.token_fixing_result=tempfile.mkstemp('_Fixing')	
			result_tmp=' echo $? > ' + self.token_fixing_result[1] + ';'

		cmd=command+';'+result_tmp
		return cmd	

	#def create_result_token	


	def unlock_process(self,wigdet):

		self.is_working=True
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Dpkg-Unlocker")
		msg=self.get_msg_text(10)
		dialog.format_secondary_text(msg)
		response=dialog.run()
		dialog.destroy()
		
		if response==Gtk.ResponseType.YES:
			self.core.processBox.manage_vterminal(True,False)
			self.unlock_button.set_sensitive(False)
			self.process_box.terminal_viewport.show()
			self.unlockInfo=self.core.unlockerManager.getUnlockerCommand()
			self.unlock_command,self.fixing_command,liveProcess=self.core.unlockerManager.getUnlockerCommand()
			#self.write_log("Dpkg-Unlocked-Gui")
			self.init_unlocker_processes()

			GLib.timeout_add(100,self.pulsate_unlock_process)

		else:
			self.is_working=False	

	#def unlock_process	


	def pulsate_unlock_process(self):

		error=False

		if not self.remove_llxup_lock_launched:
			if "Lliurex-Up" in self.unlockInfo["unlockCmd"]:
				self.process_box.terminal_label.show()
				msg=self.get_msg_text(1)
				self.write_log(msg)
				self.process_box.terminal_label.set_text(msg)
				self.remove_llxup_lock_launched=True
				self.llxup_lock_check=True
				self.exec_command("Lliurex-Up","remove")

			else:
				self.remove_llxup_lock_done=True
				self.llxup_lock_check=False
				self.llxup_result=True

		if self.remove_llxup_lock_done:
			if self.llxup_lock_check:
				self.llxup_result=self.check_process("Lliurex-Up")

			if self.llxup_result:
				
				if not self.remove_dpkg_lock_launched:
					if "Dpkg" in self.unlockInfo["unlockCmd"]:
						msg=self.get_msg_text(2)
						self.write_log(msg)
						self.process_box.terminal_label.set_text(msg)
						self.remove_dpkg_lock_launched=True
						self.dpkg_lock_check=True
						self.exec_command("Dpkg","remove")
					else:
						self.remove_dpkg_lock_done=True
						self.dpkg_lock_check=False
						self.dpkg_result=True

				if self.remove_dpkg_lock_done:
					if self.dpkg_lock_check:
						self.dpkg_result=self.check_process("Dpkg")

					if self.dpkg_result:
				
						if not self.remove_apt_lock_launched:
							if "Apt" in self.unlockInfo["unlockCmd"]:
								msg=self.get_msg_text(3)
								self.write_log(msg)
								self.process_box.terminal_label.set_text(msg)
								self.remove_apt_lock_launched=True
								self.apt_lock_check=True
								self.exec_command("Apt","remove")
							else:
								self.remove_apt_lock_done=True
								self.apt_lock_check=False
								self.apt_result=True	

						if self.remove_apt_lock_done:
							if self.apt_lock_check:
								self.apt_result=self.check_process("Apt")

							if self.apt_result:
				
								if not self.fixing_system_launched:
									if self.unlockInfo["commonCmd"]!="":
										self.process_box.terminal_label.set_text(self.get_msg_text(4))
										self.fixing_system_launched=True
										self.fixig_lock_check=True
										self.exec_command("Fixing","fixing")
									else:
										self.fixing_system_done=True
										self.fixig_lock_check=False
										self.fixing_result=True

								if self.fixing_system_done:
									if self.fixig_lock_check:
										self.fixing_result=self.check_process("Fixing")

									self.core.processBox.manage_vterminal(False,True)
									if self.fixing_result:
										msg=self.get_msg_text(5)
										self.write_log_terminal()
										self.write_log(msg)
										self.load_info(False)
										self.process_box.terminal_label.set_text(msg)
										return False
									else:
										error=True
										self.write_log_terminal()
										code=6
	
		
							else:
								error=True
								code=7			
					else:
						error=True	
						code=8								

			else:
				error=True
				code=9


			if error:
				self.core.processBox.manage_vterminal(False,True)
				msg_error=self.get_msg_text(code)
				self.process_box.terminal_label.set_name("MSG_ERROR_LABEL")
				self.process_box.terminal_label.set_text(msg_error)
				self.write_log(msg_error)
				return False


		if self.remove_llxup_lock_launched:
			if not self.remove_llxup_lock_done:
				if os.path.exists(self.token_llxup_process[1]):
					return True
				else:
					self.remove_llxup_lock_done=True
					return True	

		if self.remove_dpkg_lock_launched:
			if not self.remove_dpkg_lock_done:
				if os.path.exists(self.token_dpkg_process[1]):
					return True
				else:
					self.remove_dpkg_lock_done=True
					return True		

		if self.remove_apt_lock_launched:
			if not self.remove_apt_lock_done:
				if os.path.exists(self.token_apt_process[1]):
					return True
				else:
					self.remove_apt_lock_done=True
					return True	

		if self.fixing_system_launched:
			if not self.fixing_system_done:
				if os.path.exists(self.token_fixing_process[1]):
					return True
				else:
					self.fixing_system_done=True
					return True											
	
	#def pulsate_unlock_process
	
	def exec_command(self,action,type_cmd):

		if type_cmd=="remove":
			command=self.unlockInfo["unlockCmd"][action]
		else:
			command=self.unlockInfo["commonCmd"]

		length=len(command)
		
		if length>0:
			command=self.create_result_token(command,action)
			command=self.create_process_token(command,action)
			length=len(command)
			self.process_box.vterminal.feed_child(command,length)
		else:
			if action=="Lliurex-Up":
				self.remove_llxup_lock_done=True
			elif action=="Dpkg":
				self.remove_dpkg_lock_done=True
			elif action=="Apt":
				self.remove_ap_lock_done=True
			elif action=="Fixing":
				self.fixing_system_done=True

	#def exec_command			

	
	def check_process(self,action):

		result=True

		if action=="Lliurex-Up":
			token=self.token_llxup_result[1]
		elif action=="Dpkg":
			token=self.token_dpkg_result[1]
		elif action=="Apt":
			token=self.token_apt_result[1]
		elif action=="Fixing":
			token=self.token_fixing_result[1]
					
		
		if os.path.exists(token):
			file=open(token)
			content=file.readline()
			if '0' not in content:
				result=False
			file.close()
			os.remove(token)

		return result
		
	#def check_process

	def get_msg_text(self,code):

		if code==0:
			msg=_("All processes seem correct. Nothing to do")
		elif code==1:
			msg=_("Removing Lliurex-Up lock file...")
		elif code==2:
			msg=_("Removing Dpkg lock file...")
		elif code==3:
			msg=_("Removing Apt lock file...")
		elif code==4:
			msg=_("Fixing the system...")
		elif code==5:
			msg=_("Unlocking process finished successfully")	
		elif code==6:
			msg=_("Error fixing the system")
		elif code==7:
			msg=_("Error removing Apt lock file")
		elif code==8:
			msg=_("Error removing Dpg lock file")
		elif code==9:
			msg=_("Error removing Lliurex-Up lock file")
		elif code==10:
			msg=_("Do you want to execute the unlocking process?")
		elif code==11:
			msg=_("Some process are running. Wait a moment")
		elif code==12:
			msg=_("Detected some blocked process")
		return msg	

	#def get_msg_text									
	
	
	def quit(self,widget):

		msg_log='Quit'
		self.core.unlockerManager.cleanLockToken()
		self.write_log(msg_log)
		Gtk.main_quit()	

	#def quit	

	def write_log_terminal(self):

		init_row=self.final_row
		init_column=self.final_column

		self.final_column,self.final_row = self.process_box.vterminal.get_cursor_position()
		log_text=self.process_box.vterminal.get_text_range(init_row,init_column,self.final_row,self.final_column)[0]

		log_text=log_text.split("\n")

		syslog.openlog("DpkgUnlocker")
		syslog.syslog("Fixing the system")
				
		
		for item in log_text:
			if item!="":
				self.write_log(item)
																				
		return

	#def write_log_terminal	

	def write_log(self,msg):
	
		syslog.openlog("DpkgUnlocker")
		syslog.syslog(msg)	

	#def write_log

	def help_clicked(self,widget):

		lang=os.environ["LANG"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True
		
		if 'ca_ES' in lang:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker.'
		else:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker'

		if not run_pkexec:
			self.fcmd="su -c '%s' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
			
		self.init_threads()
		self.open_help_t.start()

	#help_clicked		
	

	def open_help(self):

		os.system(self.fcmd)

	#def open_help	
			

	def start_gui(self):
		
		Gtk.main()
		
	#def start_gui

	

#class MainWindow
from . import Core