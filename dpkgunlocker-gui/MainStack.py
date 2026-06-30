#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal()
	def __init__(self,manager):

		super().__init__()
		self.manager=manager
	
	#def __init__
		
	def run(self,*args):
		
		time.sleep(1)
		self.manager.loadInfo()
		self.infoGathered.emit()

	#def run

#class GatherInfo

class Bridge(QObject):

	currentStackChanged=Signal()
	currentOptionsStackChanged=Signal()
	feedBackCodeChanged=Signal()
	showDialogChanged=Signal()
	endProcessChanged=Signal()
	endCurrentCommandChanged=Signal()
	currentCommandChanged=Signal()
	closeGuiChanged=Signal()
	processLaunchedChanged=Signal()
	enableKonsoleChanged=Signal()
	
	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.unlockerManager=self.core.unlockerManager
		self._closeGui=False
		self._currentStack=0
		self._currentOptionsStack=0
		self._feedBackCode=0
		self._showDialog=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self.isWorked=False
		self._processLaunched=""
		self._enableKonsole=False
		self.moveToStack=""

	#def __init__

	@Property(int,notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack

	@currentStack.setter
	def currentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(int,notify=currentOptionsStackChanged)
	def  currentOptionsStack(self):

		return self._currentOptionsStack

	#def currentOptionsStack

	@currentOptionsStack.setter
	def currentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.currentOptionsStackChanged.emit()

	#def currentOptionsStack

	@Property(int,notify=feedBackCodeChanged)
	def feedBackCode(self):

		return self._feedBackCode

	#def feedBackCode

	@feedBackCode.setter
	def feedBackCode(self,feedBackCode):

		if self._feedBackCode!=feedBackCode:
			self._feedBackCode=feedBackCode
			self.feedBackCodeChanged.emit()

	#def feedBackCode

	@Property(bool,notify=showDialogChanged)
	def showDialog(self):

		return self._showDialog

	#def showDialog

	@showDialog.setter
	def showDialog(self,showDialog):

		if self._showDialog!=showDialog:
			self._showDialog=showDialog
			self.showDialogChanged.emit()
	
	#def _showDialog

	@Property(bool,notify=endProcessChanged)
	def endProcess(self):

		return self._endProcess

	#def endProcess	

	@endProcess.setter
	def endProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.endProcessChanged.emit()

	#def endProcess

	@Property(bool,notify=endCurrentCommandChanged)
	def endCurrentCommand(self):

		return self._endCurrentCommand

	#def endCurrentCommand

	@endCurrentCommand.setter
	def endCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.endCurrentCommandChanged.emit()

	#def endCurrentCommand

	@Property(str,notify=currentCommandChanged)
	def currentCommand(self):

		return self._currentCommand

	#def currentCommand

	@currentCommand.setter
	def currentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.currentCommandChanged.emit()

	#def currentCommand

	@Property(bool,notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.closeGuiChanged.emit()

	#def closeGui	

	@Property(str,notify=processLaunchedChanged)
	def processLaunched(self):

		return self._processLaunched

	#def processLaunched

	@processLaunched.setter
	def processLaunched(self,processLaunched):

		if self._processLaunched!=processLaunched:
			self._processLaunched=processLaunched
			self.processLaunchedChanged.emit()

	#def processLaunched

	@Property(bool,notify=enableKonsoleChanged)
	def enableKonsole(self):

		return self._enableKonsole

	#def enableKonsole

	@enableKonsole.setter
	def enableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.enableKonsoleChanged.emit()

	#def enableKonsole

	def initBridge(self):

		self.isWorked=True
		self.gatherInfoT=GatherInfo(self.unlockerManager)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._loadConfig)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge

	@Slot()
	def _loadConfig(self):		

		self.core.protectionStack.loadConfig()
		self.core.serviceStack.loadConfig()
			
		self.unlockerManager.writeLog("Dpkg-Unlocker-Gui")
		self.unlockerManager.writeLog(f"Initial System Metapackage Protecion. Enabled: {self.core.protectionStack.metaProtectionEnabled}")
		self.unlockerManager.writeLog(f"Initial Services Status: {self.unlockerManager.servicesData}")
		self.core.serviceStack.initWatcher()
		self.currentStack=1

	#def _loadConfig

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

		wikiUrl="https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Dpkg-Unlocker"

		realUid=os.environ.get("PKEXEC_UID") or os.environ.get("SUDO_UID")

		if realUid and os.getuid()==0:
			cmd=["sudo","-u",f"#{realUid}","gio","open",wikiUrl]
		else:
			cmd=["xdg-open",wikiUrl]

		subprocess.Popen(cmd)
		
	#def openHelp

	@Slot()
	def closeApplication(self):

		isRunningCmd=(self.core.serviceStack.runningUnlockCommand or self.core.restoreStack.runningRestoreCommand)
		
		if isRunningCmd:
			self.closeGui=False
			return

		
		if self.core.protectionStack.isProtectionChange:
			self.showDialog=True
			self.core.protectionStack.showPendingChangesDialog=True
			self.closeGui=False
			return

		if self.isWorked:
			self.core.serviceStack.statusServicesRunningTimer.stop()
		
		self.closeGui=True
		self.unlockerManager.cleanLockToken()
		self.unlockerManager.writeLog("Quit")

	#def closeApplication
	
#class Bridge

from . import Core

