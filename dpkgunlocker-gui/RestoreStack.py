#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	RESTORING_SERVICES_RUNNING=9
	RESTORING_SERVICES_SUCCESS=10
	RESTORING_SERVICES_ERROR=-12

	showRestoreStatusMessageChanged=Signal()
	runningRestoreCommandChanged=Signal()

	
	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.unlockerManager=self.core.unlockerManager
		self._showRestoreStatusMessage={"show":False,"msgCode":"","type":""}
		self._runningRestoreCommand=False

	#def __init__

	@Property(dict,notify=showRestoreStatusMessageChanged)
	def showRestoreStatusMessage(self):

		return self._showRestoreStatusMessage

	#def showRestoreStatusMessage

	@showRestoreStatusMessage.setter
	def showRestoreStatusMessage(self,showRestoreStatusMessage):

		if self._showRestoreStatusMessage!=showRestoreStatusMessage:
			self._showRestoreStatusMessage=showRestoreStatusMessage
			self.showRestoreStatusMessageChanged.emit()

	#def showRestoreStatusMessage

	@Property(bool,notify=runningRestoreCommandChanged)
	def runningRestoreCommand(self):

		return self._runningRestoreCommand

	#def runningRestoreCommand

	@runningRestoreCommand.setter
	def runningRestoreCommand(self,runningRestoreCommand):

		if self._runningRestoreCommand!=runningRestoreCommand:
			self._runningRestoreCommand=runningRestoreCommand
			self.runningRestoreCommandChanged.emit()

	#def runningRestoreCommand

	@Slot()
	def launchRestoreProcess(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.processLaunched="Restore"
		self.core.mainStack.enableKonsole=True
		self.runningRestoreCommand=True
		self.core.mainStack.endProcess=False
		self.showRestoreStatusMessage={"show":False,"msgCode":"","type":""}
		self.unlockerManager.initRestoreProcesses()
		self.unlockerManager.getRestoreCommand()
		self.unlockerManager.writeLog("Restore process launched")
		self.restoreProcessRunningTimer=QTimer(self)
		self.restoreProcessRunningTimer.timeout.connect(self._updateRestoreProcessStatus)
		self.restoreProcessRunningTimer.start(100)

	#def launchRestoreCommand

	def _updateRestoreProcessStatus(self):

		if not self.unlockerManager.restoreLaunched:
			self.core.mainStack.feedBackCode=Bridge.RESTORING_SERVICES_RUNNING
			self.unlockerManager.restoreLaunched=True
			self.core.mainStack.currentCommand=self.unlockerManager.execCommand("Restore","restore")
			self.core.mainStack.endCurrentCommand=True
			self.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
		
		if not self.unlockerManager.restoreDone:
			return self._checkProcessToken()

		self.restoreResult=self.unlockerManager.checkProcess("Restore")
								
		if self.restoreResult:
			code=Bridge.RESTORING_SERVICES_SUCCESS	
			type=self.unlockerManager.KIRIGAMI_MSG_OK
		else:
			code=Bridge.RESTORING_SERVICES_ERROR
			type=self.unlockerManager.KIRIGAMI_MSG_ERROR

		self.showRestoreStatusMessage={"show":True,"msgCode":code,"type":type}

		self.unlockerManager.writeProcessLog(code)
		self.runningRestoreCommand=False
		self.core.mainStack.endProcess=True
		self.restoreProcessRunningTimer.stop()

	#def _updateRestoreProcessStatus

	def _checkProcessToken(self):

		if self.unlockerManager.restoreLaunched and not self.unlockerManager.restoreDone:
			if not os.path.exists(self.unlockerManager.tokenRestoreProcess):
				self.unlockerManager.restoreDone=True

	#def _checkProcessToken

#class Bridge

from . import Core

