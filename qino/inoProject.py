import time
from PyQt4 import QtCore
from PyQt4.QtCore import QStringList,QString,QIODevice,QDir
from PyQt4.QtCore import pyqtSlot,QProcess,QSettings

class InoProjectException(Exception):
	def __init__(self,msg):
		self.message=msg
	def __str__(self):
		return self.message

class InoProcess(QtCore.QThread):
	def __init__(self,project,command):
		QtCore.QThread.__init__(self,project.parent())
		self.project=project		
		self.command=command
		
	
	def run(self):
		self.project.newMessage.emit()
		self.project.addMessage.emit("# running: "+self.command+"\n")
		start_time=time.time()
		self.proc = QProcess(None)
		self.proc.readyReadStandardError.connect(self.stdErrReady)
		self.proc.readyReadStandardOutput.connect(self.stdOutReady) 
		self.proc.setWorkingDirectory(self.project.path)
		commands = self.command.split(' ')
		args=QStringList()
		for cmd in commands[1:]:
			args.append(cmd)
		self.proc.start(QString(commands[0]), args, mode=QIODevice.ReadOnly)
		self.proc.waitForFinished()
		
		end_time=time.time()
		if (self.proc.exitCode()==0):
			self.project.statusChanged.emit("SUCCESS")
			self.project.addMessage.emit("# \""+self.command+"\" finished in "+str(end_time-start_time)+"sec\n")
		else:
			self.project.statusChanged.emit("FAILED")
			self.project.addErrorMessage.emit("# \""+self.command+"\" finished in "+str(end_time-start_time)+ "sec with status:"+str(self.proc.exitCode())+"\n")
	
	def stop(self):
		if self.proc!=None and self.proc.state()!=QProcess.NotRunning:
			self.project.addErrorMessage.emit("# Received stop process command\n")
			self.proc.kill()
			
	def stdErrReady(self):
		#Reading possible errors
		errors=unicode(self.proc.readAllStandardError().data(),errors='ignore')
		if (errors!=None and len(errors)>0):
			self.project.addErrorMessage.emit(QString(errors))
	def stdOutReady(self):
		msg=unicode(self.proc.readAllStandardOutput().data(),errors='ignore')
		if (msg!=None and len(msg)>0):
			self.project.addMessage.emit(QString(msg))
		
class InoProject(QtCore.QObject):
	""" SIGNALS """
	newMessage = QtCore.pyqtSignal()
	addMessage = QtCore.pyqtSignal(str)
	addErrorMessage=QtCore.pyqtSignal(str)
	statusChanged=QtCore.pyqtSignal(str)
	def __init__(self, path,parent):
		QtCore.QObject.__init__(self,parent)
		self.path=path
		self.serialPort=None
		self.modelBoard=None
		self.currentProcess=None
		self.settings = QSettings(self.path+QDir.separator()+"ino.ini",QSettings.IniFormat)
		setMB = self.settings.value("build/board-model")
		if setMB.isValid():
			self.modelBoard=setMB.toString()
	
	@pyqtSlot()
	def processFinished(self):
		self.currentProcess=None
	
	@pyqtSlot()
	def stopProcess(self):
		if self.currentProcess!=None:
			self.currentProcess.stop()
			self.currentProcess.terminate()
			
	@staticmethod
	def newProject(path):
		initProcess=QProcess(None)
		initProcess.setWorkingDirectory(path)
		initProcess.start("ino",['init'])
		initProcess.waitForFinished()
		return initProcess.exitCode()==0
		
	
	@pyqtSlot()
	def build(self):
		if self.currentProcess==None:
			self.statusChanged.emit("Building...")
			self.currentProcess=InoProcess(self,"ino build -m "+self.modelBoard)
			self.currentProcess.start()
			self.currentProcess.finished.connect(self.processFinished)
	
	@pyqtSlot()
	def upload(self):
		if self.currentProcess==None:
			self.statusChanged.emit("Uploading...")
			cmd="ino upload -m "+self.modelBoard
			if (self.serialPort!=None):
				cmd+=" -p "+self.serialPort
			self.currentProcess=InoProcess(self,cmd)
			self.currentProcess.start()
			self.currentProcess.finished.connect(self.processFinished)
	
	@pyqtSlot()
	def clean(self):
		if self.currentProcess==None:
			self.statusChanged.emit("Cleaning...")
			self.currentProcess=InoProcess(self,"ino clean")
			self.currentProcess.start()
			self.currentProcess.finished.connect(self.processFinished)
	
	def setModelBoard(self,modelBoard):
		self.modelBoard=modelBoard
		self.settings.setValue("build/board-model",modelBoard)
	
	def setSerialPort(self,serialPort):
		self.serialPort=serialPort
	
