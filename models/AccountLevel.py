import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import Base, lock_and_release, connect_and_close


class AccountLevel(Base):
    __tablename__ = "account_levels"

    level = sa.Column(sa.Integer, primary_key=True)
    amount = sa.Column(sa.Float)
    percentage = sa.Column(sa.Float)
    bonus = sa.Column(sa.Float)

    @classmethod
    @connect_and_close
    def get(
        cls,
        level: int = None,
        amount: float = None,
        s: Session = None,
    ):
        if level:
            res = s.execute(sa.select(cls).where(cls.level == level))
            try:
                return res.fetchone().t[0]
            except:
                pass
        elif amount:
            res = s.execute(
                sa.select(cls).where(cls.amount <= amount).order_by(cls.amount.desc())
            )
            try:
                return res.first().t[0]
            except:
                pass

    @classmethod
    @lock_and_release
    async def add(
        cls,
        level: int,
        amount: float,
        percentage: float,
        bonus: float,
        s: Session = None,
    ):
        s.execute(
            sa.insert(cls).values(
                level=level, amount=amount, percentage=percentage, bonus=bonus
            )
        )
