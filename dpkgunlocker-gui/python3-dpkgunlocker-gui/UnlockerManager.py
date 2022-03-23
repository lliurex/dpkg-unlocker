#!/usr/bin/python3

import dpkgunlocker.dpkgunlockermanager as DpkgUnlockerManager
import os
import sys
import syslog
import json
import codecs


class UnlockerManager:

	APPLY_CHANGES_SUCCESSFUL=10
	APPLY_CHANGES_ERROR=-10


	def __init__(self):

		self.unlockerCore=DpkgUnlockerManager.DpkgUnlockerManager()
		self.debug=True
		self.servicesData=[]
		self.sessionLang=""
		self.isThereALock=False
		self.getSessionLang()

	#def __init__


	def loadInfo(self):
		
		info=self.unlockerCore.checkingLocks()
		self.manageServiceInfo(info)

	#def loadConfig

	def manageServiceInfo(self,info):

		count=0
		okStatus=[0,1,3,4]
		runningStatus=[1,3,4]
		liveProcess=0
		self.isThereALock=False
		self.servicesData=[]

		for item in info:
			tmp={}
			tmp["serviceId"]=item
			tmp["statusCode"]=info[item]
			
			if info[item] in okStatus:
				count+=1 
			if info[item] in runningStatus:
				liveProcess+=1 

			self.servicesData.append(tmp)

		if count==len(info):
			self.isThereAlock=False
		else:
			if count==0:
				self.isThereAreLock=True
			else:
				if liveProcess==0:
					self.isThereALock=True 
				else:
					self.isThereALock=False

	#def manageServiceInfo

	def getSessionLang(self):

		lang=os.environ["LANG"]
		
		if 'valencia' in lang:
			self.sessionLang="ca@valencia"
		else:
			self.sessionLang="es"

	#def getSessionLang


#class UnlockerManager
