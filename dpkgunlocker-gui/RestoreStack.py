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
	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.unlockerManager=self.core.unlockerManager
		self._showRestoreStatusMessage=[False,"","Success"]
		self._runningRestoreCommand=False

	#def __init__

	def _getShowRestoreStatusMessage(self):

		return self._showRestoreStatusMessage

	#def _getShowRestoreStatusMessage

	def _setShowRestoreStatusMessage(self,showRestoreStatusMessage):

		if self._showRestoreStatusMessage!=showRestoreStatusMessage:
			self._showRestoreStatusMessage=showRestoreStatusMessage
			self.on_showRestoreStatusMessage.emit()

	#def _setShowRestoreStatusMessage

	def _getRunningRestoreCommand(self):

		return self._runningRestoreCommand

	#def _getRunningRestoreCommand

	def _setRunningRestoreCommand(self,runningRestoreCommand):

		if self._runningRestoreCommand!=runningRestoreCommand:
			self._runningRestoreCommand=runningRestoreCommand
			self.on_runningRestoreCommand.emit()

	#def _setRunningRestoreCommand

	def _getProcessLaunched(self):

		return self._processLaunched

	#def _getProcessLaunched

	def _setProcessLaunched(self,processLaunched):

		if self._processLaunched!=processLaunched:
			self._processLaunched=processLaunched
			self.on_processLaunched.emit()

	#def _setProcessLaunched

	@Slot()
	def launchRestoreProcess(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.processLaunched="Restore"
		self.core.mainStack.enableKonsole=True
		self.runningRestoreCommand=True
		self.core.mainStack.endProcess=False
		self.showRestoreStatusMessage=[False,"","Success"]
		Bridge.unlockerManager.initRestoreProcesses()
		Bridge.unlockerManager.getRestoreCommand()
		Bridge.unlockerManager.writeLog("Restore process launched")
		self.restoreProcessRunningTimer=QTimer(None)
		self.restoreProcessRunningTimer.timeout.connect(self._updateRestoreProcessStatus)
		self.restoreProcessRunningTimer.start(100)

	#def launchRestoreCommand

	def _updateRestoreProcessStatus(self):

		error=False

		if not Bridge.unlockerManager.restoreLaunched:
			self.core.mainStack.feedBackCode=Bridge.RESTORING_SERVICES_RUNNING
			Bridge.unlockerManager.restoreLaunched=True
			self.core.mainStack.currentCommand=Bridge.unlockerManager.execCommand("Restore","restore")
			self.core.mainStack.endCurrentCommand=True
			self.restoreCheck=True
			Bridge.unlockerManager.writeProcessLog(self.core.mainStack.feedBackCode)
		
		if Bridge.unlockerManager.restoreDone:
			if self.restoreCheck:
				self.restoreResult=Bridge.unlockerManager.checkProcess("Restore")
									
			if self.restoreResult:
				code=Bridge.RESTORING_SERVICES_SUCCESS	
			else:
				error=True
				code=Bridge.RESTORING_SERVICES_ERROR

			if error:
				self.showRestoreStatusMessage=[True,code,"Error"]
			else:
				self.showRestoreStatusMessage=[True,code,"Success"]

			Bridge.unlockerManager.writeProcessLog(code)
			self.runningRestoreCommand=False
			self.core.mainStack.endProcess=True
			self.restoreProcessRunningTimer.stop()

		if Bridge.unlockerManager.restoreLaunched:
			if not Bridge.unlockerManager.restoreDone:
				if not os.path.exists(Bridge.unlockerManager.tokenRestoreProcess[1]):
					Bridge.unlockerManager.restoreDone=True

	#def _updateRestoreProcessStatus

	on_showRestoreStatusMessage=Signal()
	showRestoreStatusMessage=Property('QVariantList',_getShowRestoreStatusMessage,_setShowRestoreStatusMessage,notify=on_showRestoreStatusMessage)
	
	on_runningRestoreCommand=Signal()
	runningRestoreCommand=Property(bool,_getRunningRestoreCommand,_setRunningRestoreCommand,notify=on_runningRestoreCommand)

#class Bridge

from . import Core

