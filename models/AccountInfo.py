import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.DB import Base, connect_and_close, lock_and_release
from models.AccountLevel import AccountLevel


class AccountInfo(Base):
    __tablename__ = "account_info"

    trader_id = sa.Column(sa.String, primary_key=True)
    country = sa.Column(sa.String)
    registery_date = sa.Column(sa.Date)
    balance = sa.Column(sa.Float)
    deposits_count = sa.Column(sa.Integer)
    deposits_sum = sa.Column(sa.Float)
    withdrawal_count = sa.Column(sa.Integer)
    withdrawal_sum = sa.Column(sa.Float)
    turnover_clear = sa.Column(sa.BigInteger)
    vol_share = sa.Column(sa.BigInteger)

    level = sa.Column(sa.Integer, default=1)
    profit_percentage = sa.Column(sa.Float)

    closed = sa.Column(sa.Boolean, default=False)

    def __str__(info):
        return f"{info.trader_id}/{info.country}/{info.registery_date}/{info.balance}/{info.deposits_count}/{info.deposits_sum}/{info.withdrawal_count}/{info.withdrawal_sum}/{info.turnover_clear}/{info.vol_share}"

    @classmethod
    @connect_and_close
    def get(cls, trader_id: str = None, trader_ids: list = None, s: Session = None):
        if trader_id:
            res = s.execute(
                sa.select(cls).where(
                    cls.trader_id == trader_id,
                )
            )
            try:
                return res.fetchone().t[0]
            except:
                pass
        elif trader_ids:
            res = s.execute(
                sa.select(cls).where(
                    cls.trader_id.in_(
                        trader_ids,
                    )
                )
            )
            try:
                return list(map(lambda x: x[0], res.tuples().all()))
            except:
                pass

    @classmethod
    @lock_and_release
    async def close(cls, trader_id: str, s: Session = None):
        s.query(cls).filter_by(trader_id=trader_id).update(
            {
                cls.closed: True,
            }
        )

    @classmethod
    @lock_and_release
    async def update_info(cls, data: dict, is_closed: bool, s: Session = None):
        acc_lv = AccountLevel.get(amount=data["turnover_clear"])
        update_dict = {
            cls.closed: is_closed,
            cls.level: acc_lv.level,
            cls.profit_percentage: acc_lv.percentage,
        }
        for k, v in data.items():
            col = getattr(cls, k, None)
            if col is None:
                continue
            update_dict[col] = v
        s.query(cls).filter_by(trader_id=data["trader_id"]).update(update_dict)

    @classmethod
    @lock_and_release
    async def update_fields(
        cls,
        trader_id: str,
        field_names: str | list[str],
        new_vals,
        s: Session = None,
    ):
        update_dict = {}
        if isinstance(field_names, str):
            update_dict[getattr(cls, field_names)] = new_vals
        else:
            for n, v in zip(field_names, new_vals):
                update_dict[getattr(cls, n)] = v
        s.query(cls).filter_by(trader_id=trader_id).update()

    @classmethod
    @lock_and_release
    async def add(
        cls,
        data: dict,
        is_closed: bool,
        s: Session = None,
    ):
        acc_lv = AccountLevel.get(amount=data["turnover_clear"])
        s.execute(
            sa.insert(cls).values(
                **data,
                level=acc_lv.level,
                profit_percentage=acc_lv.percentage,
                closed=is_closed,
            )
        )
