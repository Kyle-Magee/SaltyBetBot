import os
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(BASE_DIR, 'fighters.db'))
Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)


class Fighter(Base):
    __tablename__ = 'fighters'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    average_number_of_votes = Column(Integer, default=0)
    average_win_time = Column(Integer, default=0)
    average_loss_time = Column(Integer, default=0)

Base.metadata.create_all(engine)
