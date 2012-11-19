from uiImpl.Ui_SerialDialog import Ui_SerialDialog
from PyQt4.QtGui import QDialog,QTextCursor
from PyQt4.QtCore import QThread, pyqtSignal,pyqtSlot
import Queue
import serial
class SerialMonitor(QThread):
    '''
        Thread to manage serial connection
    '''
    newMessage=pyqtSignal(str)
    def __init__(self,parent,serialPort):
        QThread.__init__(self,parent)
        self.serialPort=serialPort
        self.queue=Queue.Queue()
        if (self.serialPort!=None):
            print ("serial: "+self.serialPort)
            self.serial=serial.Serial(str(self.serialPort),9600)
            self.running=True
        else:
            self.serial=None
            self.running=False
    def run(self):
        if (self.serial!=None):
            while self.running:
                msg=self.serial.readline()
                if (msg):
                    self.newMessage.emit("<: "+msg)
                else:
                    pass
        else:
            self.newMessage.emit("ERROR: No serialPort defined")
    
    def sendMessage(self,msg):
        if (self.running and self.serial!=None and self.serial.isOpen()):
            self.serial.write(str(msg))
            self.newMessage.emit(">: "+msg+"\n")
    
    def stop(self):
        self.running=False
        if (self.serial!=None and self.serial.isOpen()):
            print ("serial closed")
            self.serial.close()

class SerialDialog(QDialog):
    def __init__(self,serialPort,parent):
        QDialog.__init__(self,parent)
        self.ui=Ui_SerialDialog()
        self.ui.setupUi(self)
        self.serialPort=serialPort
        self.serialMonitor=SerialMonitor(self,self.serialPort)
        self.serialMonitor.newMessage.connect(self.addMessage)
        self.serialMonitor.start()
        self.ui.sendBtn.clicked.connect(self.sendMessage)
        self.ui.sendEdit.returnPressed.connect(self.sendMessage)
        
    @pyqtSlot(str)
    def addMessage(self,msg):
        self.ui.serialEdit.textCursor().insertText(msg)
        c = self.ui.serialEdit.textCursor();
        c.movePosition(QTextCursor.End);
        self.ui.serialEdit.setTextCursor(c);
    
    @pyqtSlot()
    def sendMessage(self):
        self.serialMonitor.sendMessage(self.ui.sendEdit.text())
        self.ui.sendEdit.clear()
    
    def closeEvent(self, *args, **kwargs):
        if (self.serialMonitor!=None and self.serialMonitor.isRunning()):
            self.serialMonitor.stop()
            self.serialMonitor.terminate()
            self.addMessage("Serial Process terminating...")
            while (not self.serialMonitor.wait()):
                pass
            print ("serialMonitor terminated")
        return QDialog.closeEvent(self, *args, **kwargs)
    