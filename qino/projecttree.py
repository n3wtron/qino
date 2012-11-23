from PyQt4.QtGui import QTreeView,QAction,QMessageBox,QIcon,QInputDialog,QKeySequence
from PyQt4.QtCore import QDir,QString,QFile
class ProjectTree(QTreeView):
    def __init__(self,parent):
        QTreeView.__init__(self,parent)
        
        newFolderAction=QAction(QIcon.fromTheme("folder-new"),"New Folder",self)
        newFolderAction.triggered.connect(self.newFolder)
        self.addAction(newFolderAction)
        
        deleteAction=QAction(QIcon.fromTheme("edit-delete"),"Delete",self)
        deleteAction.setShortcut(QKeySequence.Delete)
        deleteAction.triggered.connect(self.deleteFile)
        self.addAction(deleteAction)
    
    def newFolder(self):
        print self.sender().__class__.__name__
        index = self.currentIndex()
        if self.model()!=None:
            newDir=QInputDialog.getText(self, QString("New Directory"), QString("Directory name"))
            if newDir[1]:
                finfo=self.model().fileInfo(index)
                if (finfo.isDir()):
                    QDir(finfo.absoluteFilePath()).mkdir(newDir[0])
                else:
                    finfo.dir().mkdir(newDir[0])
    
    def deleteDir(self,dirPath):
        dr = QDir(dirPath)
        result=True
        if (dr.exists()):
            for entry in dr.entryInfoList(filters=QDir.NoDotAndDotDot.__or__(QDir.Hidden).__or__(QDir.AllDirs).__or__(QDir.Files) , sort=QDir.NoSort):
                if entry.isDir():
                    result&=self.deleteDir(entry.absoluteFilePath())
                else:
                    result&=QFile.remove(entry.absoluteFilePath())
            dr.rmdir(dirPath)
        return result
    
    def deleteFile(self):
        selModel=self.selectionModel()
        selIndexes =  selModel.selectedRows()
        fileNames=""
        for index in selIndexes:
            finfo=self.model().fileInfo(index)
            fileNames+=" "+finfo.baseName()+"."+finfo.completeSuffix()
        delRes=QMessageBox.question(self, QString("Delete"), QString("Are you sure to delete %1").arg(fileNames), buttons=QMessageBox.Yes , defaultButton=QMessageBox.No)
        if delRes==QMessageBox.Yes:
            for index in selIndexes:
                finfo=self.model().fileInfo(index)
                if (finfo.isDir()):
                    if (not self.deleteDir(finfo.absoluteFilePath())):
                        QMessageBox.critical(self, QString("Delete"), QString("Error cannot delete %1").arg(finfo.absoluteFilePath()), buttons=QMessageBox.Ok, defaultButton=QMessageBox.Cancel)    
                else:
                    if (not QFile(finfo.absoluteFilePath()).remove()):
                        QMessageBox.critical(self, QString("Delete"), QString("Error cannot delete %1").arg(finfo.absoluteFilePath()), buttons=QMessageBox.Ok, defaultButton=QMessageBox.Cancel)