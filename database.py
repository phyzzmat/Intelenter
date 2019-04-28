from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    topic = Column(String)
    room = Column(String)
    statement = Column(String(5000))
    answer = Column(String(5000))
    points = Column(Integer)


class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True)
    number = Column(String,
                    ForeignKey('question.room'),
                    nullable=False)
    password = Column(String)


base_name = 'base.db'
engine = create_engine('sqlite:///{}'.format(base_name))
session = sessionmaker()
session.configure(bind=engine)
session = session()
Base.metadata.create_all(engine)
