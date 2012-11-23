# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/serialdialog.ui'
#
# Created: Mon Nov 19 15:19:20 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SerialDialog(object):
    def setupUi(self, SerialDialog):
        SerialDialog.setObjectName(_fromUtf8("SerialDialog"))
        SerialDialog.resize(400, 298)
        self.gridLayout = QtGui.QGridLayout(SerialDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.sendBtn = QtGui.QPushButton(SerialDialog)
        self.sendBtn.setObjectName(_fromUtf8("sendBtn"))
        self.gridLayout.addWidget(self.sendBtn, 2, 4, 1, 1)
        self.serialEdit = QtGui.QPlainTextEdit(SerialDialog)
        self.serialEdit.setUndoRedoEnabled(False)
        self.serialEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.serialEdit.setReadOnly(True)
        self.serialEdit.setPlainText(_fromUtf8(""))
        self.serialEdit.setObjectName(_fromUtf8("serialEdit"))
        self.gridLayout.addWidget(self.serialEdit, 0, 0, 1, 5)
        self.cleanConsoleBtn = QtGui.QToolButton(SerialDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-clear"))
        self.cleanConsoleBtn.setIcon(icon)
        self.cleanConsoleBtn.setObjectName(_fromUtf8("cleanConsoleBtn"))
        self.gridLayout.addWidget(self.cleanConsoleBtn, 1, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 1)
        self.sendEdit = QtGui.QLineEdit(SerialDialog)
        self.sendEdit.setObjectName(_fromUtf8("sendEdit"))
        self.gridLayout.addWidget(self.sendEdit, 2, 0, 1, 4)

        self.retranslateUi(SerialDialog)
        QtCore.QObject.connect(self.cleanConsoleBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.serialEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(SerialDialog)

    def retranslateUi(self, SerialDialog):
        SerialDialog.setWindowTitle(QtGui.QApplication.translate("SerialDialog", "Serial Monitor", None, QtGui.QApplication.UnicodeUTF8))
        self.sendBtn.setText(QtGui.QApplication.translate("SerialDialog", "Send", None, QtGui.QApplication.UnicodeUTF8))
        self.cleanConsoleBtn.setText(QtGui.QApplication.translate("SerialDialog", "...", None, QtGui.QApplication.UnicodeUTF8))

