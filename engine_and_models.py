from sqlalchemy import create_engine, DateTime
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from config import config_local, config_server_1, config_server_2, test_mode

Base = declarative_base()
Base_server_1 = declarative_base()
Base_server_2 = declarative_base()


class Goip(Base_server_1):
    __tablename__ = 'goip'
    id = Column(Integer, primary_key=True)
    prefix = Column(String(16))
    sost = Column(Integer)


class Prov(Base_server_2):
    __tablename__ = 'prov'
    id = Column(Integer, primary_key=True)
    prefix = Column(String(16))
    minsim = Column(Integer)
    maxsim = Column(Integer)


class Tasks(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    command = Column(String(20))
    channel = Column(Integer)
    subchannel = Column(Integer)
    time = Column(DateTime)

    def __repr__(self):
        return f"<Task(id={self.id}, command='{self.command}', channel={self.channel}, subchannel={self.subchannel}, time='{self.time}')>"


class Assignment(Base):
    __tablename__ = 'assignment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(Integer, unique=True, nullable=False)
    working_time = Column(Integer, nullable=False)
    pause_time = Column(Integer, nullable=False)
    subchannel = Column(String(150), nullable=False)
    in_work = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"channel={self.channel}, working_time={self.working_time}, pause_time={self.pause_time},subchannel={self.subchannel}"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)


engine = create_engine(config_local)
engine_server_1 = create_engine(config_server_1)
engine_server_2 = create_engine(config_server_2)

if __name__ == "__main__":
    if test_mode:
        Base.metadata.create_all(engine)
        Base_server_1.metadata.create_all(engine_server_1)
        Base_server_2.metadata.create_all(engine_server_2)
    else:
        Base.metadata.create_all(engine)
