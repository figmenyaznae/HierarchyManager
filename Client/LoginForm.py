#!/usr/bin/python2.7
#This file is the first module for the HierarchyManager App. Use it to launch it in debug mode.

import sys
from PyQt4 import QtGui, QtCore, uic
from sqlalchemy import and_
from FolderView import *
from DbConfig import *
from DbModel import *
from utils import *
import base64


class RegisterForm(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("RegisterForm.ui", self)
        self.connect(self.ui.acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.ui.declineButton, QtCore.SIGNAL("clicked()"), self.close)
        
        self.session = Session()
    
    def accept(self):
        login = wrapNone(self.ui.usernameEdit.text())
        password = wrapNone(self.ui.passwordEdit.text())
        password_confirm = wrapNone(self.ui.passwordEdit_2.text())
        first_name = wrapNone(self.ui.nameEdit.text())
        last_name = wrapNone(self.ui.surnameEdit.text())
        if (login is not None and password==password_confirm):
            user = User(login=login, password=password, first_name=first_name, last_name=last_name)
            self.session.add(user)
            self.session.commit()
            self.close()
        else:
            QtGui.QMessageBox.critical(self, "Error", "Passwords does not match!")
        
class LoginForm(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("LoginForm.ui", self)
        
        self.connect(self.ui.enterButton, QtCore.SIGNAL("clicked()"), self.tryToLogin)
        self.connect(self.ui.registerButton, QtCore.SIGNAL("clicked()"), self.register)
                
        with open('session.conf') as f:
            s = base64.b64decode(f.read())
            login = s[:20].rstrip()
            password = s[20:].rstrip()
            self.loginEdit.setText(login)
            self.passwordEdit.setText(password)
            self.ui.rememberMe.setChecked(True)
            
        self.session = Session()
        if self.session is None:
            QtGui.QMessageBox.critical(self, "Error", "Database not connected. You will not be able to log in.")
    
    def register(self):
        self.register = RegisterForm(self)
        self.register.open()
    
    def tryToLogin(self):
        try:
            login = str(self.loginEdit.text())
            password = str(self.passwordEdit.text())
            user_id = self.session.query(User.id).filter(and_(User.login==login, User.password==password)).one_or_none()
            if user_id == None:
                QtGui.QMessageBox.critical(self, "Error", "Wrong username/password")
            else:
                if self.ui.rememberMe.checkState() == QtCore.Qt.Checked:
                    with open('session.conf', 'w') as f:
                        f.write(base64.b64encode('{:<20}{:<20}'.format(login, password)))
                self.view = FolderView(self, user_id[0])
                self.view.show()
                self.hide()
        except Exception as e:
            print e
            QtGui.QMessageBox.critical(self, "Error", "Database Error")
            

def Start():
    app = QtGui.QApplication(sys.argv)
    form = LoginForm()
    form.show()
    app.exec_()
    
if __name__ == "__main__":
    Start()