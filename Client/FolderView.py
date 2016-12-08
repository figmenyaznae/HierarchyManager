#!/usr/bin/python2.7

from PyQt4 import QtGui, QtCore, QtSql, uic
from sqlalchemy import and_
from FolderModel import *
from FolderProperties import *
from FileProperties import *
from DbConfig import *
from DbModel import *
from utils import *
FolderIDRole = QtCore.Qt.UserRole


class FolderView(QtGui.QDialog):
    def __init__(self, parent, UserID, sharedOnly = False, otherUser = 0):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("FolderView.ui", self)
        
        self.Other = otherUser
        self.user = UserID
        self.sharedOnly = sharedOnly
        self.parent = parent
        self.folder = 0
        self.file = 0
        self.copy = None
        
        self.session = Session()
        
        self.CommentsModel = QtGui.QStringListModel()
        self.ui.comentsList.setModel(self.CommentsModel)
        
        self.model = FolderModel()
        self.model.setDataList(self.execQuery())
        
        home = QtGui.QListWidgetItem('Home >')
        home.setData(FolderIDRole,0)
        self.ui.history.addItem(home)
        self.ui.history.setCurrentItem(self.ui.history.item(0))
        
        self.ui.mainView.setModel(self.model)
        self.ui.mainView.doubleClicked.connect(self.doubleClicked)
        self.ui.mainView.customContextMenuRequested.connect(self.ItemContextMenu)
        self.ui.mainView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.ui.history.itemClicked.connect(self.selectFolder)
        
        self.connect(self.ui.submitComment, QtCore.SIGNAL("clicked()"), self.createComment)
        
        self.ui.frame.setVisible(False)
        
    def execQuery(self):
        list = []
        if self.folder==0:
            if self.sharedOnly:
                for node in self.session.query(Node).filter(and_(
                        Node.user_id==self.user,
                        Node.parent==None,
                        Node.is_shared
                    )):
                    list.append(FolderItem(*(1, node.id, node.name)))
            else:
                for node in self.session.query(Node).filter(and_(Node.user_id==self.user, Node.parent==None)):
                    list.append(FolderItem(*(1, node.id, node.name)))
                    
                for user in self.session.query(User).all():
                    if self.session.query(Node).filter(and_(
                        Node.user == user,
                        Node.is_shared
                    )).count()>0 and user.id != self.user:
                        list.append(FolderItem(*(0, user.id, user.login)))
        else:
            parent = self.session.query(Node).filter(Node.id==self.folder).one()
            children = [node.id for node in parent.children]
            files = [file.id for file in parent.files]
            if self.sharedOnly:
                for node in (
                    self.session.query(Node)
                    .filter(
                        and_(
                            Node.user_id==self.user,
                            Node.id.in_(children),
                            Node.is_shared
                        )
                    )
                ):
                    list.append(FolderItem(*(1, node.id, node.name), is_shared = node.is_shared))
                    
                for file in self.session.query(File).filter(and_(
                    File.id.in_(files),
                    File.is_shared
                )):
                    list.append(FolderItem(
                        2,
                        file.id,
                        file.name,
                        extractIcon(file.extension),
                        getRaiting(file),
                        file.is_shared
                    ))
            else:
                for node in self.session.query(Node).filter(and_(
                        Node.user_id==self.user,
                        Node.id.in_(children)
                    )):
                    list.append(FolderItem(*(1, node.id, node.name, ''), is_shared=node.is_shared))
                    
                for file in self.session.query(File).filter(File.id.in_(files)):
                    list.append(FolderItem(
                        2,
                        file.id,
                        file.name,
                        extractIcon(file.extension),
                        getRaiting(file),
                        file.is_shared
                    ))
        return list
    
    def createComment(self):
        self.session.add(Comment(text = wrapNone(self.ui.myComment.text()), user_id = self.user, file_id = self.file))
        self.session.commit()
        self.ui.myComment.clear()
        self.CommentsModel.setStringList(self.commentQuery(self.file))
    
    def commentQuery(self, file_id):
        list = []
        file = self.session.query(File).filter(File.id==self.file).one()
        for comment in file.comments:
            if comment.user.first_name is None and comment.user.last_name is None:
                list.append('{}: {}'.format(comment.user.login, comment.text))
            else:
                list.append('{} {}: {}'.format(comment.user.first_name, comment.user.last_name, comment.text))
        return list
    
    def doubleClicked(self, index):
        self.ui.frame.setVisible(False)
        type = self.model.data(index, ItemTypeRole)
        
        self.model.setDataList(self.execQuery())
        if type==0:
            self.otherView = FolderView(self, self.model.data(index, ItemIDRole), True, self.user)
            self.otherView.open()
            if self.otherView.copy is not None:
                self.copy = self.otherView.copy
        elif type==1:
            self.folder = self.model.data(index, ItemIDRole)
            folder = QtGui.QListWidgetItem(self.model.data(index, ItemNameRole)+" >")
            folder.setData(FolderIDRole,self.folder)
            self.ui.history.addItem(folder)
            self.ui.history.setCurrentItem(self.ui.history.item(self.ui.history.count()-1))
            self.model.setDataList(self.execQuery())
        else:
            self.file = self.model.data(index, ItemIDRole)
            self.ui.fileName.setText("File: " + self.model.data(index, ItemNameRole))
            self.ui.rating.setText("Rating: " + ratingStr(self.model.data(index, ItemRatingRole)))
            self.ui.shared.setText("Shared: " + str(self.model.data(index, ItemIsSharedRole)))
            self.CommentsModel.setStringList(self.commentQuery(self.file))
            self.ui.frame.setVisible(True)
        
    def selectFolder(self, item):
        self.ui.frame.setVisible(False)
        self.folder = item.data(FolderIDRole).toInt()[0]
        self.model.setDataList(self.execQuery())
        hist = [ (
                self.ui.history.item(i).text(),
                self.ui.history.item(i).data(FolderIDRole).toInt()[0]
            ) for i in xrange(self.ui.history.currentRow()+1)]
        self.ui.history.clear()
        for item in hist:
            folder = QtGui.QListWidgetItem(item[0])
            folder.setData(FolderIDRole,item[1])
            self.ui.history.addItem(folder)
        self.ui.history.setCurrentItem(self.ui.history.item(self.ui.history.count()-1))
    
    def ItemContextMenu(self, point):
        self.fileAddMenu = QtGui.QMenu()
        if not self.sharedOnly:
            self.fileAddMenu.addAction("Add folder", self.folderAdd)
            if self.folder != 0:
                self.fileAddMenu.addAction("Add file", self.fileAdd)
        if len(self.ui.mainView.selectedIndexes())>0:
            self.fileAddMenu.addAction("Copy", self.objCopy)
        if not self.sharedOnly and self.copy!=None:
            self.fileAddMenu.addAction("Paste", self.objPaste)
        if not self.sharedOnly and len(self.ui.mainView.selectedIndexes())>0:
            self.fileAddMenu.addAction("Delete", self.objDelete)    
        self.fileAddMenu.popup(self.mapToGlobal(point))
    
    def folderAdd(self):
        self.FP = FolderProperties(self, self.folder, self.user)
        self.FP.open()
    
    def fileAdd(self):
        self.FP = FileProperties(self, self.folder)
        self.FP.open()
        
    def objCopy(self):
        indexes = self.ui.mainView.selectedIndexes()
        self.copy = []
        for i in indexes:
            type = self.model.data(i, ItemTypeRole)
            if type!=0:
                rec = {'Type':type, 'ID':self.model.data(i, ItemIDRole)}
                self.copy.append(rec)
    
    def objPaste(self):
        if self.copy!=None:
            parent = self.session.query(Node).filter(Node.id==self.folder).one()
            for index in self.copy:
                if index['Type'] == 1:
                    child = self.session.query(Node).filter(Node.id==index['ID']).one()
                    
                    parent.children.append(child)
                    self.session.commit()
                    
                elif index['Type'] == 2:
                    child = self.session.query(File).filter(File.id==index['ID']).one()
                    
                    parent.files.append(child)
                    self.session.commit()
        
        self.model.setDataList(self.execQuery())
        
    def objDelete(self):
        indexes = self.ui.mainView.selectedIndexes()
        parent = self.session.query(Node).filter(Node.id==self.folder).one_or_none()
        
        for i in indexes:
            type = self.model.data(i, ItemTypeRole)
            id = self.model.data(i, ItemIDRole)
            if type==1:
                child = self.session.query(Node).filter(Node.id==id).one()
                
                if parent is not None:
                    parent.children.remove(child)
                    self.session.commit()
                
                if len(child.parent)==0:
                    self.session.delete(child)
                    self.session.commit()
                    
            elif type==2:
                child = self.session.query(File).filter(File.id==id).one()
                
                parent.files.remove(child)
                self.session.commit()
                
                if len(child.folders)==0:
                    self.session.delete(child)
                    self.session.commit()
                    
        self.model.setDataList(self.execQuery())
