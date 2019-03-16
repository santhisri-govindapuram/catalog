import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class PilgrimageName(Base):
    __tablename__ = 'pilgrimagename'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="pilgrimagename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class StateName(Base):
    __tablename__ = 'statename'
    id = Column(Integer, primary_key=True)
    name = Column(String(370), nullable=False)
    address = Column(String(160))
    god = Column(String(24))
    area = Column(String(270))
    date = Column(DateTime, nullable=False)
    pilgrimagenameid = Column(Integer, ForeignKey('pilgrimagename.id'))
    pilgrimagename = relationship(
        PilgrimageName, backref=backref('statename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="statename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'address': self. address,
            'god': self. god,
            'area': self. area,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///pilgrimages.db')
Base.metadata.create_all(engin)
