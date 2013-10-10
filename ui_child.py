# -*- coding: utf-8 -*-
 
# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Thu Oct 10 12:39:09 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!
import ui as appui
from PyQt4 import QtCore, QtGui
 
 
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
 
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
 
 
class Ui_Custom_Form(appui.Ui_Form):
 
    def __init__(self):
        super(Ui_Custom_Form, self).__init__()
       
        self.listWidget.setVisible(False)
 
        QtCore.QObject.connect(self.listWidget, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")), self.stackedWidget.setCurrentIndex)
 
    #def childMethod(self):
 
        #super(Ui_Custom_Form, self).__init__()