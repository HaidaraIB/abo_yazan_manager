import sqlalchemy as sa
from sqlalchemy.orm import Session
import sqlalchemy.exc as exc
from models.DB import Base, connect_and_close, lock_and_release


class Referral(Base):
    __tablename__ = "referrals"
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    user_id = sa.Column(sa.BigInteger)
    referral_trader_id = sa.Column(sa.BigInteger, unique=True)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.current_timestamp())

    @classmethod
    @lock_and_release
    async def add(
        cls,
        user_id: int,
        referral_trader_id: str,
        s: Session = None,
    ):
        s.execute(
            sa.insert(cls).values(
                user_id=user_id,
                referral_trader_id=referral_trader_id,
            ).prefix_with("OR IGNORE")
        )


    @classmethod
    @connect_and_close
    def get(
        cls,
        referral_trader_id: str = None,
        user_id: int = None,
        s: Session = None,
    ):
        if user_id:
            res = s.execute(sa.select(cls).where(cls.user_id == user_id))
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass
        elif referral_trader_id:
            res = s.execute(
                sa.select(cls).where(cls.referral_trader_id == referral_trader_id)
            )
            try:
                return res.fetchone().t[0]
            except:
                pass
