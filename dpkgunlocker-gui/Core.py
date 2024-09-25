#!/usr/bin/env python3

import sys


from . import UnlockerManager
from . import ProtectionStack
from . import RestoreStack
from . import ServiceStack
from . import MainStack

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

	
		self.unlockerManager=UnlockerManager.UnlockerManager()
		self.protectionStack=ProtectionStack.Bridge()
		self.restoreStack=RestoreStack.Bridge()
		self.serviceStack=ServiceStack.Bridge()
		self.mainStack=MainStack.Bridge()
		
		self.mainStack.initBridge()
	
		
	#def init

	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
