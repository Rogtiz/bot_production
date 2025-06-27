from sqlalchemy import select, insert, update, delete

from app.dao.base import BaseDAO
from app.gwent.models import Players, OverallWinRate, RankWinRate, TopWinrate
from app.database import async_session_maker


class WinrateDAO(BaseDAO):
    @classmethod
    async def get_by_period(self, start_date, end_date):
        async with async_session_maker() as session:
            stmt = select(self.model).where(
                self.model.date >= start_date,
                self.model.date <= end_date
            )
            return (await session.execute(stmt)).scalars().all()


class PlayersDAO(BaseDAO):
    model = Players

    @classmethod
    async def add_player_if_not_exists(self, player_id):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.gwent_id == player_id)
            result = await session.execute(stmt)
            player = result.scalar_one_or_none()
            if not player:
                stmt = insert(self.model).values(gwent_id=player_id).returning(self.model)
                result = await session.execute(stmt)
                await session.commit()
                return result.scalars().first()
            return player


class OverallWinRateDAO(WinrateDAO):
    model = OverallWinRate


class RankWinRateDAO(WinrateDAO):
    model = RankWinRate


class TopWinrateDAO(WinrateDAO):
    model = TopWinrate