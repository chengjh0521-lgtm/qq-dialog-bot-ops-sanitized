"""脱敏的跨部门数据契约；不定义任何策略字段或计算规则。"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, PositiveInt


class MinuteBarIn(BaseModel):
    instrument: str = Field(min_length=1, max_length=32)
    observed_at: datetime
    close: Decimal = Field(gt=0)


class OpaqueSignalIn(BaseModel):
    signal_id: str = Field(min_length=1, max_length=80)
    produced_at: datetime
    payload: dict[str, Any]


class ManualOperationIn(BaseModel):
    occurred_at: datetime
    side: Literal["BUY", "SELL"]
    quantity: PositiveInt
    price: Decimal = Field(gt=0)


class PositionOut(BaseModel):
    user_id: str
    instrument: str
    quantity: int
    updated_at: datetime
