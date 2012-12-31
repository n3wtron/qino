from PyQt4.QtCore import QString,pyqtSlot,QDir,QFile,QIODevice,QProcess,QModelIndex,QSettings,Qt
from PyQt4.QtGui import QMainWindow,QFileDialog,QMessageBox,QAction,QTextCursor,QTextCharFormat
from PyQt4.QtGui import QActionGroup,QMenu,QFileSystemModel
from uiImpl.Ui_MainWindow import Ui_MainWindow
from inoProject import InoProject
from codeeditor import CodeEditor
from serialdialog import SerialDialog

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.ui = Ui_MainWindow()
		self.tabMap={}
		self.serialDialog=None
		self.ui.setupUi(self)
		self.ui.tabWidget.currentChanged.connect(self.tabChanged)
		self.ui.action_Close.triggered.connect(self.closeCurrentTab)
		self.ui.tabWidget.tabCloseRequested.connect(self.tabClosed)
		self.ui.action_Open_Project.triggered.connect(self.openProject)
		self.ui.action_New_Project.triggered.connect(self.newProject)
		
		self.settings=QSettings("alpha01","qino")
		
		#Refresh Serial Ports and Arduino Boards Menu
		self.boardActs={}
		self.getBoardVersions()
		self.serialMenu=QMenu("Serial Port")
		refreshSerialAction=QAction(QString("Refresh"),self)
		self.serialMenu.addAction(refreshSerialAction)
		refreshSerialAction.triggered.connect(self.refreshSerialPorts)
		self.serialGroup=QActionGroup(self)
		self.ui.menu_Build.addMenu(self.serialMenu)
		self.ui.action_Serial_Monitor.triggered.connect(self.openSerialMonitor)
		self.project=None
		self.refreshSerialPorts()
		#load recent project
		self.refreshRecentOpenedProject()
		
		
	def getBoardVersions(self):
		boardVersionProc=QProcess()
		boardVersionProc.start("ino",["list-models"], mode=QIODevice.ReadOnly)
		self.boardModels=[]
		self.boardDesc=[]
		while (boardVersionProc.waitForReadyRead()):
			line=QString(boardVersionProc.readLine(maxlen=0))
			while (line!=""):
				parts=line.split(":")
				if (len(parts)==2):
					self.boardModels.append(parts[0].trimmed())
					self.boardDesc.append(parts[1].trimmed())
				line=QString(boardVersionProc.readLine(maxlen=0))
		boardVersionProc.waitForFinished()
		
		buildForMenu = QMenu("Boards",self)
		self.buildForActionGrp = QActionGroup(self)
		for i in range(0,len(self.boardModels)):
			act=QAction(self.boardModels[i],self)
			self.boardActs[self.boardModels[i]]=act
			act.setCheckable(True)
			act.triggered.connect(self.setBoardModel)
			if (self.boardDesc[i].contains("DEFAULT")):
				act.setChecked(True)
			act.setToolTip(self.boardDesc[i])
			self.buildForActionGrp.addAction(act)
			buildForMenu.addAction(act)
		self.ui.menu_Build.addMenu(buildForMenu)
	
	def refreshSerialPorts(self):
		devDir=QDir("/dev")
		searches=["ttyACM*"]
		results=devDir.entryList(searches,filters=QDir.System)
		for act in self.serialGroup.actions():
			self.serialGroup.removeAction(act)
			self.serialMenu.removeAction(act)
		for res in results:
			act=QAction(devDir.absolutePath()+QDir.separator()+res,self.serialMenu)
			act.setCheckable(True)
			act.triggered.connect(self.setSerialPort)
			self.serialGroup.addAction(act)
			self.serialMenu.addAction(act)
		if len(results)>0:
			self.serialGroup.actions()[0].setChecked(True)
			self.setSerialPort()
			
	def setBoardModel(self):
		if (self.project!=None):
			print "setBoardModel called"
			self.project.setModelBoard(self.buildForActionGrp.checkedAction().text())
	
	def setSerialPort(self):
		if (self.project!=None):
			if (len(self.serialGroup.actions())==0):
				self.project.setSerialPort(None)
			else:
				self.project.setSerialPort(self.serialGroup.checkedAction().text())
	
	def cleanConsole(self):
		currPalete = self.ui.consoleOut.palette()
		self.ui.consoleOut.setPalette(currPalete)
		self.ui.consoleOut.clear()
	
	def addMessage(self,message):
		self.ui.consoleOut.textCursor().insertText(message)
		c = self.ui.consoleOut.textCursor();
		c.movePosition(QTextCursor.End);
		self.ui.consoleOut.setTextCursor(c);
			
	def addErrorMessage(self,message):
		cur = self.ui.consoleOut.textCursor()
		redFormat=QTextCharFormat()
		redFormat.setForeground(Qt.red)
		cur.setCharFormat(redFormat)
		cur.insertText(message)
		cur.movePosition(QTextCursor.End)
		blackFormat=QTextCharFormat()
		blackFormat.setForeground(Qt.black)
		cur.setCharFormat(blackFormat)
		self.ui.consoleOut.setTextCursor(cur)
	
	def newProject(self):
		projectDir=QFileDialog.getExistingDirectory(self, caption=QString("New Project"))
		if (projectDir!=''):
			prjDir=QDir(projectDir)
			if (len(prjDir.entryInfoList())>2):
				QMessageBox.critical(self, QString("New Project"), QString("The directory %1 must be empty").arg(projectDir), buttons=QMessageBox.Ok, defaultButton=QMessageBox.Cancel)
			else:
				if not InoProject.newProject(projectDir) :
					QMessageBox.critical(self, QString("New Project"), QString("Error creating %1 project").arg(projectDir), buttons=QMessageBox.Ok, defaultButton=QMessageBox.Cancel)
				else:	
					self.unsetProject()
					self.setProject(projectDir)
				
	def newFile(self):
		newFileName=QFileDialog.getSaveFileName(self, caption=QString("new File"),directory=self.project.path)
		if (newFileName!=''):
			nf = QFile(newFileName)
			if (not nf.exists()):
				nf.open(QIODevice.WriteOnly)
				nf.close()
			
	def refreshRecentOpenedProject(self):
		self.settings.beginGroup("recentProject")
		recentProjects=self.settings.value("projects").toStringList()
		if self.project!=None:
			if not recentProjects.contains(self.project.path):
				if recentProjects.count()==5:
					recentProjects.removeAt(4)
				recentProjects.insert(0,self.project.path)
				self.settings.setValue("projects",recentProjects)
		#create menu
		self.ui.menuRecently_Opened.clear()
		for prj in self.settings.value("projects").toList():
			act=QAction(prj.toString(),self)
			act.triggered.connect(self.openRecentProject)
			self.ui.menuRecently_Opened.addAction(act)
		self.settings.endGroup()
				
	def setProject(self,path):
		self.project=InoProject(path,self)
		# add to recent opened project
		self.refreshRecentOpenedProject()
		self.setSerialPort()
		""" Actions """
		self.ui.action_Build.triggered.connect(self.project.build)
		self.ui.action_Clean.triggered.connect(self.project.clean)
		self.ui.action_Upload.triggered.connect(self.project.upload)
		self.ui.action_Save.triggered.connect(self.save)
		self.project.addMessage.connect(self.addMessage)
		self.project.addErrorMessage.connect(self.addErrorMessage)
		self.project.newMessage.connect(self.cleanConsole)
		self.project.statusChanged.connect(self.statusChanged)
		self.ui.projectTree.doubleClicked.connect(self.openFile)
		self.ui.action_New.triggered.connect(self.newFile)
		self.ui.stopBtn.clicked.connect(self.project.stopProcess)
		#Loading FS
		fsModel = QFileSystemModel(self)
		fsModel.setReadOnly(False)
		fsModel.setRootPath(self.project.path)
		self.ui.projectTree.setModel(fsModel)
		self.ui.projectTree.setRootIndex(fsModel.index(self.project.path));
		#modelboard
		if (self.project.modelBoard==None):
			self.setBoardModel()
		else:
			self.boardActs[self.project.modelBoard].setChecked(True)
		self.tabMap={}
		self.setWindowTitle("QIno - "+self.project.path)
	
	def unsetProject(self):
		allClosed=True
		if (self.project!=None):
			for _ in range(0,self.ui.tabWidget.count()):
				if (not self.tabClosed(0) ):
					allClosed=False
					break
			if (allClosed):
				self.ui.action_Build.triggered.disconnect(self.project.build)
				self.ui.action_Clean.triggered.disconnect(self.project.clean)
				self.ui.action_Upload.triggered.disconnect(self.project.upload)
				self.ui.action_Save.triggered.disconnect(self.save)
				self.project.addMessage.disconnect(self.addMessage)
				self.project.addErrorMessage.disconnect(self.addErrorMessage)
				self.project.newMessage.disconnect(self.cleanConsole)
				self.ui.projectTree.doubleClicked.disconnect(self.openFile)
				self.ui.action_New.triggered.disconnect(self.newFile)
				self.ui.stopBtn.clicked.disconnect(self.project.stopProcess)
				self.project.statusChanged.disconnect(self.statusChanged)
				self.statusChanged("No Project loades")
				self.project=None
		return allClosed
	
	def save(self):
		if (not self.currentCodeEditor is None ):
			if (self.currentCodeEditor.fileName is None):
				fileName = QFileDialog.getSaveFileName(self, "Save",filter=QString("Ino source (*.ino)"),directory=QString(self.project.path))
				if (fileName!=''):
					self.currentCodeEditor.save(fileName)
			else:
				self.currentCodeEditor.save()
			
	def openProject(self):
		projectDir=QFileDialog.getExistingDirectory(self, caption=QString("Open Project"))
		if (projectDir!=''):
			self.unsetProject()
			self.setProject(projectDir)
			
	@pyqtSlot()
	def openRecentProject(self):
		if self.sender()!=None:
			if self.unsetProject():
				self.setProject(self.sender().text())
	
	@pyqtSlot(int)
	def tabChanged(self,tabIndex):
		self.currentCodeEditor=self.ui.tabWidget.widget(tabIndex)
	
	@pyqtSlot(int)
	def tabClosed(self,tabIndex):
		editor=self.ui.tabWidget.widget(tabIndex)
		if (not editor.document().isModified()):
			self.ui.tabWidget.removeTab(tabIndex)
			del(self.tabMap[editor.fileName])
		else:
			fileName=editor.fileName
			resp=QMessageBox.question(self, QString("Close File %1").arg(fileName), QString("Do you want save %1 before close it?").arg(fileName), QMessageBox.Yes,QMessageBox.No,QMessageBox.Cancel )
			if (resp==QMessageBox.Yes):
				editor.save()
				self.ui.tabWidget.removeTab(tabIndex)
				del(self.tabMap[editor.fileName])
			if (resp==QMessageBox.No):
				self.ui.tabWidget.removeTab(tabIndex)
				del(self.tabMap[editor.fileName])
			if (resp==QMessageBox.Cancel):
				return False
		return True
	
	@pyqtSlot()
	def closeCurrentTab(self):
		if (self.ui.tabWidget.currentIndex()!=-1):
			self.tabClosed(self.ui.tabWidget.currentIndex())
	
	@pyqtSlot(QModelIndex)
	def openFile(self,index):
		if (index.isValid() and not self.ui.projectTree.model().isDir(index)):
			fileName=self.ui.projectTree.model().filePath(index)
			#search already opened files
			if not fileName in self.tabMap:
				editor=CodeEditor(self.ui.tabWidget)
				editor.modificationChanged.connect(self.documentChanged)
				self.ui.tabWidget.addTab(editor, fileName)
				self.tabMap[fileName]=editor
				editor.open(fileName)
			self.ui.tabWidget.setCurrentWidget(self.tabMap[fileName])
	
	@pyqtSlot(bool)
	def documentChanged(self,modified):
		editor=self.sender()
		currFileName=QString(editor.fileName)
		if (modified):
			self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(editor),QString(currFileName.replace(self.project.path,"")+'*'))
		else:
			self.ui.tabWidget.setTabText(self.ui.tabWidget.indexOf(editor),QString(currFileName.replace(self.project.path,"")))
	
	@pyqtSlot()
	def openSerialMonitor(self):
		if self.serialDialog==None:
			if self.project!=None:
				serialPort=self.project.serialPort
			else:
				if (len(self.serialGroup.actions())==0):
					serialPort=None
				else:
					serialPort=self.serialGroup.checkedAction().text();
			self.serialDialog=SerialDialog(serialPort,None)
			self.serialDialog.show()
		else:
			if (self.serialDialog.isVisible()):
				self.serialDialog.activateWindow()
			else:
				self.serialDialog=None
				self.openSerialMonitor()
	
	@pyqtSlot(str)
	def statusChanged(self,status):
		self.ui.statusBar.showMessage(status)
	
	def closeEvent(self,event):
		if (self.unsetProject()):
			QMainWindow.closeEvent(self,event)
			if self.serialDialog!=None:
				self.serialDialog.close()
		else:
			event.ignore()
	
