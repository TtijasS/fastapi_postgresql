from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ItemBrief(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(BaseModel):
    email: str
    name: str

class CustomerRead(CustomerCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    customer_id: int
    price_eur: float
    notes: str | None = None

class OrderRead(BaseModel):
    id: int
    customer_id: int
    price_eur: float
    notes: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StoreBase(BaseModel):
    name: str
    location: str

class StoreCreate(StoreBase):
    item_ids: list[int] = []

class StoreRead(StoreBase):
    id: int
    items: list[ItemBrief] = []
    model_config = ConfigDict(from_attributes=True)

class StoreItemsUpdate(StoreBase):
    item_ids: list[int]

class HeatPumpData(BaseModel):
    id: int
    date_time: datetime
    i_1: float
    i_2: float
    i_3: float
    v_1: float
    v_2: float
    v_3: float
    r_1: float
    r_2: float
    r_3: float