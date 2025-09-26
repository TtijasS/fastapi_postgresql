from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(BaseModel):
    email: str
    name: str

class CustomerRead(CustomerCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
