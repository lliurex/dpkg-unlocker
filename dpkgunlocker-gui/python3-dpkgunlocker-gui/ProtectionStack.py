#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import pwd
signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	META_PROTECTION_ENABLED=6
	META_PROTECTION_DISABLED=7
	META_PROTECTION_CHANGE_SUCCESS=8
	META_PROTECTION_ENABLED_ERROR=-10
	META_PROTECTION_DISABLED_ERROR=-11
	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.unlockerManager=self.core.unlockerManager
		self._metaProtectionEnabled=True
		self._showProtectionStatusMessage=[False,"","Success"]
		self._isProtectionChange=False
		self._showPendingChangesDialog=False
		self._showProtectionOption=False


	#def __init__

	def loadConfig(self):		

		self.metaProtectionEnabled=Bridge.unlockerManager.metaProtectionEnabled
		self.showProtectionOption=Bridge.unlockerManager.showProtectionOption()

		if self.metaProtectionEnabled:
			self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_ENABLED,"Success"]
		else:
			self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_DISABLED,"Warning"]

		self._copyCurrentProtectionStatus()
	
	#def loadConfig

	def updateProtectionInfo(self):

		if not self.isProtectionChange:
			self.metaProtectionEnabled=Bridge.unlockerManager.metaProtectionEnabled
			if self.metaProtectionEnabled:
				self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_ENABLED,"Success"]
			else:
				self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_DISABLED,"Warning"]

			self._copyCurrentProtectionStatus()

	#def updateProtection Info

	def _getMetaProtectionEnabled(self):

		return self._metaProtectionEnabled

	#def _getFeedBackCode

	def _setMetaProtectionEnabled(self,metaProtectionEnabled):

		if self._metaProtectionEnabled!=metaProtectionEnabled:
			self._metaProtectionEnabled=metaProtectionEnabled
			self.on_metaProtectionEnabled.emit()

	#def _setMetaProtectionEnabled

	def _getShowProtectionStatusMessage(self):

		return self._showProtectionStatusMessage

	#def _getShowServiceStatusMesage

	def _setShowProtectionStatusMessage(self,showProtectionStatusMessage):

		if self._showProtectionStatusMessage!=showProtectionStatusMessage:
			self._showProtectionStatusMessage=showProtectionStatusMessage
			self.on_showProtectionStatusMessage.emit()

	#def _setShowProtectionStatusMessage

	def _getIsProtectionChange(self):

		return self._isProtectionChange

	#def _getIsProtectionChange

	def _setIsProtectionChange(self,isProtectionChange):

		if self._isProtectionChange!=isProtectionChange:
			self._isProtectionChange=isProtectionChange
			self.on_isProtectionChange.emit()
	
	#def _setIsProtectionChange

	def _getShowPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def _getShowPendingChangesDialog

	def _setShowPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog!=showPendingChangesDialog:
			self._showPendingChangesDialog=showPendingChangesDialog
			self.on_showPendingChangesDialog.emit()
	
	#def _setShowPendingChangesDialog

	def _getShowProtectionOption(self):

		return self._showProtectionOption

	#def _getShowProtectionOption

	def _setShowProtectionOption(self,showProtectionOption):

		if self._showProtectionOption!=showProtectionOption:
			self._showProtectionOption=showProtectionOption
			self.on_showProtectionOption.emit()

	#def _setShowProtectionOption

	def _copyCurrentProtectionStatus(self):

		self.currentMetaProtectionStatus=copy.deepcopy(self.metaProtectionEnabled)
		self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)

	#def _copyCurrentProtectionStatus

	@Slot(bool)
	def getProtectionChange(self,change):
		
		if self.currentMetaProtectionStatus!=change:
			self.metaProtectionEnabled=change
			self.showProtectionStatusMessage=[False,"","Success"]
			self.isProtectionChange=True
		else:
			self.metaProtectionEnabled=self.currentMetaProtectionStatus
			self.showProtectionStatusMessage=self.currentMessage
			self.isProtectionChange=False

	#def getProtectionChange

	@Slot()
	def changeProteccionStatus(self):

		self.core.mainStack.showDialog=False
		self.core.mainStack.isWorked=True
		self.core.mainStack.runningUnlockCommand=True
		self.isProtectionChange=False
		self.showPendingChangesDialog=False

		result=Bridge.unlockerManager.changeMetaProtectionStatus(self.metaProtectionEnabled)
		if result:
			self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_CHANGE_SUCCESS,"Success"]
			self.currentMessage=copy.deepcopy(self.showProtectionStatusMessage)
			self.core.mainStack.closeGui=True
		else:
			if self.metaProtectionEnabled:
				self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_DISABLED_ERROR,"Error"]
			else:
				self.showProtectionStatusMessage=[True,Bridge.META_PROTECTION_ENABLED_ERROR,"Error"]
			self.core.mainStack.closeGui=False
			self.core.mainStack.moveToStack=""

		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.core.mainStack.moveToStack=""
		
		Bridge.unlockerManager.getMetaProtectionStatus()	
		self._copyCurrentProtectionStatus()
		Bridge.unlockerManager.writeLog("Final System Metapackage Protecion. Enabled: %s"%(str(self.metaProtectionEnabled)))
		
		self.core.mainStack.isWorked=False	
		self.core.mainStack.runningUnlockCommand=False

	#def changeProteccionStatus

	@Slot()
	def discardChangeProtectionStatus(self):

		self.core.mainStack.showDialog=False
		self.showPendingChangesDialog=False
		self.isProtectionChange=False
		self.metaProtectionEnabled=self.currentMetaProtectionStatus
		self.showProtectionStatusMessage=self.currentMessage
		self.core.mainStack.closeGui=True
		if self.core.mainStack.moveToStack!="":
			self.core.mainStack.currentOptionsStack=self.core.mainStack.moveToStack
			self.core.mainStack.moveToStack=""

	#def discardChangeProtectionStatus

	on_metaProtectionEnabled=Signal()
	metaProtectionEnabled=Property(int,_getMetaProtectionEnabled,_setMetaProtectionEnabled,notify=on_metaProtectionEnabled)
	
	on_showProtectionStatusMessage=Signal()
	showProtectionStatusMessage=Property('QVariantList',_getShowProtectionStatusMessage,_setShowProtectionStatusMessage,notify=on_showProtectionStatusMessage)

	on_isProtectionChange=Signal()
	isProtectionChange=Property(bool,_getIsProtectionChange,_setIsProtectionChange,notify=on_isProtectionChange)

	on_showPendingChangesDialog=Signal()
	showPendingChangesDialog=Property(bool,_getShowPendingChangesDialog,_setShowPendingChangesDialog,notify=on_showPendingChangesDialog)
	
	on_showProtectionOption=Signal()
	showProtectionOption=Property(bool,_getShowProtectionOption,_setShowProtectionOption,notify=on_showProtectionOption)
	
#class Bridge

from . import Core

