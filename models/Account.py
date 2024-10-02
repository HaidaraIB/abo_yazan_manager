import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import Base, lock_and_release, connect_and_close


class Account(Base):
    __tablename__ = "accounts"

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey("users.id"), primary_key=True)
    trader_id = sa.Column(sa.String, sa.ForeignKey("account_info.trader_id"))
    withdrawals = sa.Column(sa.Float, default=0)

    @classmethod
    @connect_and_close
    def get(
        cls,
        user_id: int = None,
        trader_id: int = None,
        s: Session = None,
    ):
        if user_id:
            res = s.execute(sa.select(cls).where(cls.user_id == user_id))
        elif trader_id:
            res = s.execute(sa.select(cls).where(cls.trader_id == trader_id))
        try:
            return res.fetchone().t[0]
        except:
            pass

    @classmethod
    @lock_and_release
    async def attach_to_user(
        cls,
        user_id: int,
        trader_id: str,
        s: Session = None,
    ):
        s.execute(
            sa.insert(cls).values(
                user_id=user_id,
                trader_id=trader_id,
            )
        )

    @classmethod
    @lock_and_release
    async def reattach_to_user(
        cls,
        user_id: int,
        trader_id: str,
        s: Session = None,
    ):
        s.query(cls).filter_by(user_id=user_id).update(
            {
                cls.trader_id: trader_id,
            }
        )

    @classmethod
    @lock_and_release
    async def withdraw(
        cls,
        user_id: int,
        amount: float,
        s: Session = None,
    ):
        s.query(cls).filter_by(user_id=user_id).update(
            {
                cls.withdrawals: cls.withdrawals - amount,
            }
        )
