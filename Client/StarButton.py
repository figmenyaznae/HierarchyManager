from PyQt4 import QtGui, QtCore
from sqlalchemy import and_
from DbConfig import *
from DbModel import *
from utils import *

class StarButton(QtGui.QPushButton):
    def __init__(self, parent = None, value = 0):
        QtGui.QPushButton.__init__(self, parent)
        self.ratingValue = value
        
    def clicked(self):
        print self.ratingValue
        QtGui.QPushButton.clicked()
        
class RatingDialog(QtGui.QDialog):
    def __init__(self, parent, user, file):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Set Raiting")
        self.resize(80,30)
        self.user = user
        self.file = file
        self.session = Session()
        
        self.buttons = [StarButton(self, i + 1) for i in xrange(5)]
        
        layout = QtGui.QHBoxLayout()
        for button in self.buttons:
            button.setFlat(True)
            button.setFont(QtGui.QFont('Wingdings', 16))
            button.setText(u"\xb6")
            layout.addWidget(button)
            
        self.connect(self.buttons[0], QtCore.SIGNAL("clicked()"), self.set1Star)
        self.connect(self.buttons[1], QtCore.SIGNAL("clicked()"), self.set2Star)
        self.connect(self.buttons[2], QtCore.SIGNAL("clicked()"), self.set3Star)
        self.connect(self.buttons[3], QtCore.SIGNAL("clicked()"), self.set4Star)
        self.connect(self.buttons[4], QtCore.SIGNAL("clicked()"), self.set5Star)
        
        self.setLayout(layout)
        
    def set1Star(self):
        self.setStar(1)
    def set2Star(self):
        self.setStar(2)
    def set3Star(self):
        self.setStar(3)
    def set4Star(self):
        self.setStar(4)
    def set5Star(self):
        self.setStar(5)
     
    def setStar(self, value):
        file = self.session.query(Rating).filter(and_(
            Rating.user_id==self.user,
            Rating.file_id==self.file
        )).one_or_none()
        
        if file is None:
            self.session.add(Rating(value=value, user_id=self.user, file_id=self.file))
        else:
            file.value=value
        self.session.commit()
        
        self.parent().model.setDataList(self.parent().execQuery())
        self.parent().ui.rating.setText(ratingStr(file.value))
        self.close()