from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class FileExtension(Base):
    __tablename__ = 'FileExtensions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mask = Column(String)
    icon = Column(String)

    def __repr__(self):
       return "<FileExtension(name='%s', mask='%s', icon='%s')>" % (self.mask, self.extension, self.icon)

class File(Base):
    __tablename__ = 'Files'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    extension_id = Column(ForeignKey('FileExtensions.id'))
    extension = relationship('FileExtension')
    path = Column(String)
    is_shared = Column(Boolean)

    def __repr__(self):
       return "<File(name='%s', extension='%d', path='%s', isShared='%r')>" % (self.name, self.extension_id, self.path, is_shared)
    
class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    login = Column(String(20))
    password = Column(String(20))
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    def __repr__(self):
       return "<User(login='%s', password='%s', first_name='%s', last_name='%s')>" % (self.login, self.password, self.first_name, self.last_name)

edges_table = Table('Edges', Base.metadata,
    Column('child_id', Integer, ForeignKey('Nodes.id')),
    Column('parent_id', Integer, ForeignKey('Nodes.id'))
)

node_files_table = Table('NodeFiles', Base.metadata,
    Column('node_id', Integer, ForeignKey('Nodes.id')),
    Column('file_id', Integer, ForeignKey('Files.id'))
)

class Node(Base):
    __tablename__ = 'Nodes'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(ForeignKey('Users.id'))
    user = relationship('User')
    is_shared = Column(Boolean)
    parent = relationship('Node', secondary=edges_table, primaryjoin=edges_table.c.child_id==id, secondaryjoin=edges_table.c.parent_id==id, backref='children')
    files = relationship('File', secondary=node_files_table, backref='folders')

    def __repr__(self):
        return "<Node(name='%s', user_id='%d', isShared='%r')>" % (self.name, self.user_id, self.is_shared)

class Comment(Base):
    __tablename__ = 'Comments'
    
    id = Column(Integer, primary_key=True)
    text = Column(String)
    user_id = Column(ForeignKey('Users.id'))
    user = relationship('User')
    file_id = Column(ForeignKey('Files.id'))
    file = relationship('File', backref='comments')
    
    def __repr__(self):
        return "<Comment(name='%s', user_id='%d', file_id='%d')>" % (self.text, self.user_id, self.file_id)
