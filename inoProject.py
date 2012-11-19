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
		proc = QProcess(None)
		proc.setWorkingDirectory(self.project.path)
		proc.setProcessChannelMode(QProcess.MergedChannels)
		commands = self.command.split(' ')
		args=QStringList()
		for cmd in commands[1:]:
			args.append(cmd)
		proc.start(QString(commands[0]), args, mode=QIODevice.ReadOnly)
		while (proc.waitForReadyRead()):
			self.project.addMessage.emit(QString(proc.readAll()))
		proc.waitForFinished()
		
		end_time=time.time()
		if (proc.exitCode()==0):
			self.project.addMessage.emit("# \""+self.command+"\" finished in "+str(end_time-start_time)+"sec\n")
		else:
			self.project.addErrorMessage.emit("\""+self.command+"\" finished in "+str(end_time-start_time)+ "sec with status:"+str(proc.exitCode())+"\n")
	
class InoProject(QtCore.QObject):
	""" SIGNALS """
	newMessage = QtCore.pyqtSignal()
	addMessage = QtCore.pyqtSignal(str)
	addErrorMessage=QtCore.pyqtSignal(str)
	def __init__(self, path,parent):
		QtCore.QObject.__init__(self,parent)
		self.path=path
		self.serialPort=None
		self.modelBoard=None
		self.settings = QSettings(self.path+QDir.separator()+"ino.ini",QSettings.IniFormat)
		setMB = self.settings.value("build/board-model")
		if setMB.isValid():
			self.modelBoard=setMB.toString()
	
	@pyqtSlot()
	def init(self):
		initProcess=InoProcess(self,"ino init")
		initProcess.start()
	
	@pyqtSlot()
	def build(self):
		buildProcess=InoProcess(self,"ino build -m "+self.modelBoard)
		buildProcess.start()
	
	@pyqtSlot()
	def upload(self):
		cmd="ino upload -m "+self.modelBoard
		if (self.serialPort!=None):
			cmd+=" -p "+self.serialPort
		uploadProcess=InoProcess(self,cmd)
		uploadProcess.start()
	
	@pyqtSlot()
	def clean(self):
		cleanProcess=InoProcess(self,"ino clean")
		cleanProcess.start()
	
	def setModelBoard(self,modelBoard):
		self.modelBoard=modelBoard
		self.settings.setValue("build/board-model",modelBoard)
	
	def setSerialPort(self,serialPort):
		self.serialPort=serialPort
	