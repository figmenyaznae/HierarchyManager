from sqlalchemy import create_engine
engine = create_engine('sqlite:///test.db', echo=True)

from sqlalchemymodel import *
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

user = User(login='user', password='pass', first_name='Daniil', last_name='Zinevich')
base = Node(name='base', user=user, is_shared=True)
session.add_all([ user, base,
        Node(name='child 1', user=user, is_shared=True, parent=[base]),
        Node(name='child 2', user=user, is_shared=False, parent=[base]),
        File(name='file 1', is_shared=True, folders=[base])
    ])
session.commit()