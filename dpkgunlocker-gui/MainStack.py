#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		

	def run(self,*args):
		
		time.sleep(1)
		Bridge.unlockerManager.loadInfo()

	#def run

#class GatherInfo

class Bridge(QObject):

	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.unlockerManager=self.core.unlockerManager
		self._closeGui=False
		self._closePopUp=True
		self._currentStack=0
		self._currentOptionsStack=0
		self._feedBackCode=0
		self._showDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self.isWorked=False
		self._processLaunched=""
		self.moveToStack=""

	#def __init__

	def initBridge(self):

		self.isWorked=True
		self.gatherInfo=GatherInfo()
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._loadConfig)

	#def initBridge

	def _loadConfig(self):		

		self.core.protectionStack.loadConfig()
		self.core.serviceStack.loadConfig()
			
		Bridge.unlockerManager.writeLog("Dpkg-Unlocker-Gui")
		Bridge.unlockerManager.writeLog("Initial System Metapackage Protecion. Enabled: %s"%(str(self.core.protectionStack.metaProtectionEnabled)))
		Bridge.unlockerManager.writeLog("Initial Services Status: %s"%(str(Bridge.unlockerManager.servicesData)))
		self.core.serviceStack.initWatcher()
		self.currentStack=1

	#def _loadConfig

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getCurrentOptionsStack(self):

		return self._currentOptionsStack

	#def _getCurrentOptionsStack

	def _setCurrentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.on_currentOptionsStack.emit()

	#def _setCurrentOptionsStack

	def _getFeedBackCode(self):

		return self._feedBackCode

	#def _getFeedBackCode

	def _setFeedBackCode(self,feedBackCode):

		if self._feedBackCode!=feedBackCode:
			self._feedBackCode=feedBackCode
			self.on_feedBackCode.emit()

	#def _setFeedBackCode

	def _getShowDialog(self):

		return self._showDialog

	#def _getShowDialog

	def _setShowDialog(self,showDialog):

		if self._showDialog!=showDialog:
			self._showDialog=showDialog
			self.on_showDialog.emit()
	
	#def _setShowDialog

	def _getEndProcess(self):

		return self._endProcess

	#def _getEndProcess	

	def _setEndProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.on_endProcess.emit()

	#def _setEndProcess

	def _getEndCurrentCommand(self):

		return self._endCurrentCommand

	#def _getEndCurrentCommand

	def _setEndCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.on_endCurrentCommand.emit()

	#def _setEndCurrentCommand

	def _getCurrentCommand(self):

		return self._currentCommand

	#def _getCurrentCommand

	def _setCurrentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.on_currentCommand.emit()

	#def _setCurrentCommand

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui	

	def _getProcessLaunched(self):

		return self._processLaunched

	#def _getProcessLaunched

	def _setProcessLaunched(self,processLaunched):

		if self._processLaunched!=processLaunched:
			self._processLaunched=processLaunched
			self.on_processLaunched.emit()

	#def _setProcessLaunched

	@Slot()
	def openDialog(self):
		
		self.showDialog=True

	#def openDialog

	@Slot()
	def getNewCommand(self):

		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot() 
	def cancelAction(self):

		self.showDialog=False
		if self.core.protectionStack.showPendingChangesDialog:
			self.core.protectionStack.showPendingChangesDialog=False
			self.moveToStack=""

	#def cancelAction

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.moveToStack=stack
			if self.core.protectionStack.isProtectionChange:
				self.showDialog=True
				self.core.protectionStack.showPendingChangesDialog=True
			else:
				self.currentOptionsStack=stack
				self.moveToStack=""
	
	#def manageTransitions

	@Slot()
	def openHelp(self):
		
		runPkexec=False
		
		if "PKEXEC_UID" in os.environ:
			runPkexec=True

		if 'valencia' in Bridge.unlockerManager.sessionLang:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker.'
		else:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker'
		
		if not runPkexec:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		
		self.openHelpT=threading.Thread(target=self._openHelp)
		self.openHelpT.daemon=True
		self.openHelpT.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.helpCmd)

	#def _openHelp

	@Slot()
	def closeApplication(self):

		if self.core.serviceStack.runningUnlockCommand or self.core.restoreStack.runningRestoreCommand:
			self.closeGui=False
		else:
			if not self.core.protectionStack.isProtectionChange:
				if self.isWorked:
					self.core.serviceStack.statusServicesRunningTimer.stop()
				self.closeGui=True
				Bridge.unlockerManager.cleanLockToken()
				Bridge.unlockerManager.writeLog("Quit")
			else:
				self.showDialog=True
				self.core.protectionStack.showPendingChangesDialog=True
				self.closeGui=False

	#def closeApplication
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)

	on_feedBackCode=Signal()
	feedBackCode=Property(int,_getFeedBackCode,_setFeedBackCode,notify=on_feedBackCode)
	
	on_showDialog=Signal()
	showDialog=Property(bool,_getShowDialog,_setShowDialog,notify=on_showDialog)
	
	on_endProcess=Signal()
	endProcess=Property(bool,_getEndProcess,_setEndProcess, notify=on_endProcess)

	on_endCurrentCommand=Signal()
	endCurrentCommand=Property(bool,_getEndCurrentCommand,_setEndCurrentCommand, notify=on_endCurrentCommand)

	on_currentCommand=Signal()
	currentCommand=Property('QString',_getCurrentCommand,_setCurrentCommand, notify=on_currentCommand)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	on_processLaunched=Signal()
	processLaunched=Property('QString',_getProcessLaunched,_setProcessLaunched,notify=on_processLaunched)
	
#class Bridge

from . import Core

