from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Double, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Players(Base):
    __tablename__ = "players"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nickname = Column(String, unique=True)
    gwent_id = Column(String, unique=True, nullable=False)


class OverallWinRate(Base):
    __tablename__ = "overall_win_rate"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nilfgaard_wr = Column(Double, nullable=False)
    monsters_wr = Column(Double, nullable=False)
    skellige_wr = Column(Double, nullable=False)
    northern_realms_wr = Column(Double, nullable=False)
    syndicate_wr = Column(Double, nullable=False)
    scoiatael_wr = Column(Double, nullable=False)
    players_count = Column(Integer)
    date = Column(DateTime)


class RankWinRate(Base):
    __tablename__ = "rank_win_rate"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=False)
    nilfgaard_wr = Column(Double, nullable=False)
    monsters_wr = Column(Double, nullable=False)
    skellige_wr = Column(Double, nullable=False)
    northern_realms_wr = Column(Double, nullable=False)
    syndicate_wr = Column(Double, nullable=False)
    scoiatael_wr = Column(Double, nullable=False)
    players_count = Column(Integer)
    date = Column(DateTime)


class TopWinrate(Base):
    __tablename__ = "top_win_rate"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nilfgaard_wr = Column(Double, nullable=False)
    monsters_wr = Column(Double, nullable=False)
    skellige_wr = Column(Double, nullable=False)
    northern_realms_wr = Column(Double, nullable=False)
    syndicate_wr = Column(Double, nullable=False)
    scoiatael_wr = Column(Double, nullable=False)
    players_count = Column(Integer)
    date = Column(DateTime)
