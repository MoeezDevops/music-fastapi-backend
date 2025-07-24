from sqlalchemy import Column, ForeignKey, LargeBinary, Text
from models.base import Base
from sqlalchemy.orm import relationship


class Favourite(Base):
    __tablename__='favourite'

    id=Column(Text,primary_key=True)
    song_id=Column(Text,ForeignKey('songs.id'))
    user_id=Column(Text,ForeignKey('users.id'))

    song = relationship('SongModel')

    user = relationship('User',back_populates='favorites')

    

