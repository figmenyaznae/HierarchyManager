from sqlalchemy import create_engine
engine = create_engine('sqlite:///test.db', echo=True)

from DbModel import *
Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

user = User(login='user', password='pass', first_name='Daniil', last_name='Zinevich')
base = Node(name='base', user=user, is_shared=True)
node = Node(name='child 1', user=user, is_shared=True, parent=[base])
category = FileExtension(mask = '*.avi *.mov *.mkv', name = 'Video file', icon = 'video.png')
file = File(name='file 1', is_shared=True, folders=[base, node], user=user)
session.add_all([ user, base, category, node, file,
        Node(name='child 2', user=user, is_shared=False, parent=[base, node]),
        File(name='file 2', is_shared=False, folders=[base], extension=category, user=user),
        Comment(text='Bullshit', user=user, file = file),
        FileExtension(mask = '*.bmp *.jpeg *.jpg *.png', name = 'Image'),
        Rating(value = 1, user = user, file = file),
        User(login='user2', password='pass')
    ])
session.commit()