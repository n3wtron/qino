from PyQt4.QtGui import QPlainTextEdit,QTextEdit,QPainter,QTextFormat,QColor,QWidget,QSyntaxHighlighter,QTextCharFormat,QFont
from PyQt4.QtCore import pyqtSlot,QChar,QRect,QString,Qt,QFile,QIODevice,QRegExp,QSize
from PyQt4 import QtCore

class LineNumberArea(QWidget):
    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.codeEditor=parent
        
    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(),0)
    
    def paintEvent(self,event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self,parent):
        QPlainTextEdit.__init__(self,parent)
        self.lineNumberArea=LineNumberArea(self)
        self.setTabStopWidth(20)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self.highlighter=CHighlighter(self.document())
        
    def lineNumberAreaPaintEvent(self,event):
        painter=QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        block =self.firstVisibleBlock()
        blockNumber= block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while (block.isValid() and top <= event.rect().bottom()):
            if (block.isValid and bottom >= event.rect().top()):
                number=QString.number(blockNumber+1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0,top,self.lineNumberArea.width(),self.fontMetrics().height(),QtCore.Qt.AlignRight,number)
            block=block.next()
            top=bottom
            bottom=top+self.blockBoundingRect(block).height()
            blockNumber+=1
    
    def lineNumberAreaWidth(self):
        digits=1
        dMax=max(1,self.blockCount())
        while (dMax>=10):
            dMax/=10
            digits+=1
        return 3+self.fontMetrics().width(QChar('9'))*digits
        
    def resizeEvent(self,event):
        QPlainTextEdit.resizeEvent(self,event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(),cr.top(),self.lineNumberAreaWidth(),cr.height()))
        
    @pyqtSlot(int)
    def updateLineNumberAreaWidth(self,newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        
    @pyqtSlot()
    def highlightCurrentLine(self):
        extraSelections = []
        if (not self.isReadOnly()):
            lineColor = QColor("#E0EEEE")
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection,True)
            selection.cursor=self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
        
    @pyqtSlot(QRect,int)
    def updateLineNumberArea(self,rect,dy):
        if (dy!=0):
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0,rect.y(),self.lineNumberArea.width(),rect.height())
        if (rect.contains(self.viewport().rect())):
            self.updateLineNumberAreaWidth(0)
    
    def keyPressEvent(self,event):
        #AutoTab
        numTab=0
        if (event.key()==Qt.Key_Enter or event.key()==16777220):
            #new line
            newBlock=self.textCursor().block()
            currLine=newBlock.text()
            tabRE=QRegExp("^[\t]*")
            tabRE.indexIn(currLine)
            numTab=tabRE.matchedLength()
            if (currLine.trimmed().right(1)=="{"):
                numTab+=1
        QPlainTextEdit.keyPressEvent(self,event)
        if (numTab>0):
            for _ in range(0,numTab):
                currLine=self.textCursor().insertText("\t")
    
    def open(self,fileName):
        self.fileName=fileName
        srcFile=QFile(fileName)    
        srcFile.open(QIODevice.ReadOnly)
        self.setPlainText(QString(srcFile.readAll()))
        srcFile.close()
        self.document().setModified(False)
        
    def save(self,fileName=None):
        if (fileName is None):
            fileName=self.fileName
        inoFile = QFile(fileName)
        inoFile.open(QIODevice.WriteOnly)
        inoFile.write(self.toPlainText().toAscii())
        inoFile.close()
        self.document().setModified(False)
        
class CHighlighter(QSyntaxHighlighter):
    def __init__(self,parent):
        QSyntaxHighlighter.__init__(self,parent)
        self.rules=[]
        self.keywordFormat=QTextCharFormat()
        self.singleLineCommentFormat=QTextCharFormat()
        self.multiLineCommentFormat=QTextCharFormat()
        self.quotaFormat=QTextCharFormat()
        self.functionFormat=QTextCharFormat()
        self.precompilerFormat=QTextCharFormat()
        self.numberFormat=QTextCharFormat()
        
        self.keywordFormat.setForeground(Qt.darkBlue)
        self.keywordFormat.setFontWeight(QFont.Bold)
        
        keywords=[]
        keywords.append("\\bclass\\b")
        keywords.append("\\bconst\\b")
        keywords.append("\\bdouble\\b")
        keywords.append("\\benum\\b")
        keywords.append("\\bexplicit\\b")
        keywords.append("\\bfriend\\b")
        keywords.append("\\binline\\b")
        keywords.append("\\bint\\b")
        keywords.append("\\blong\\b")
        keywords.append("\\bnamespace\\b")
        keywords.append("\\boperator\\b")
        keywords.append("\\bprivate\\b")
        keywords.append("\\bprotected\\b")
        keywords.append("\\bpublic\\b")
        keywords.append("\\bshort\\b")
        keywords.append("\\bsignals\\b")
        keywords.append("\\bsigned\\b")
        keywords.append("\\bslots\\b")
        keywords.append("\\bstatic\\b")
        keywords.append("\\bstruct\\b")
        keywords.append("\\btemplate\\b")
        keywords.append("\\btypedef\\b")
        keywords.append("\\btypename\\b")
        keywords.append("\\bunion\\b")
        keywords.append("\\bunsigned\\b")
        keywords.append("\\bvirtual\\b")
        keywords.append("\\bvoid\\b")
        keywords.append("\\bvolatile\\b") 
        for kw in keywords:
            self.rules.append((QRegExp(kw),self.keywordFormat))
        
        self.numberFormat.setForeground(Qt.darkRed)
        self.rules.append((QRegExp("\\d+"),self.numberFormat))
        
        self.quotaFormat.setForeground(Qt.darkGreen)
        self.rules.append((QRegExp("\".*\""),self.quotaFormat))
        
        self.functionFormat.setFontItalic(True);
        self.functionFormat.setForeground(Qt.blue);
        self.rules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),self.functionFormat))
        
        self.singleLineCommentFormat.setForeground(Qt.red);
        self.rules.append((QRegExp("//[^\n]*"),self.singleLineCommentFormat))
        self.commentStartExpression = QRegExp("/\\*");
        self.commentEndExpression = QRegExp("\\*/");
        
        self.multiLineCommentFormat.setForeground(Qt.lightGray)
        
        self.precompilerFormat.setForeground(Qt.darkCyan)
        self.rules.append((QRegExp("^[ |\t]*#.*"),self.precompilerFormat))
        
    def highlightBlock(self,text):
        for rule in self.rules:
            re=rule[0]
            index=re.indexIn(text)
            while (index >=0):
                length=re.matchedLength()
                self.setFormat(index,length,rule[1])
                index=re.indexIn(text,index+length)
        self.setCurrentBlockState(0)
        
        startIndex=0
        if (self.previousBlockState()!=1):
            startIndex=self.commentStartExpression.indexIn(text)
        while (startIndex >=0 ):
            endIndex=self.commentEndExpression.indexIn(text,startIndex)
            if (endIndex==-1):
                self.setCurrentBlockState(1)
                commentLength=text.length()-startIndex
            else:
                commentLength=endIndex-startIndex+self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex=self.commentStartExpression.indexIn(text,startIndex+commentLength)
    