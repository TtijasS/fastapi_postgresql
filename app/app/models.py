# app/app/models.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Numeric, Table, UniqueConstraint, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base
from typing import List, Optional

item_store = Table(
    "item_store",
    Base.metadata,
    # CASCADE is used fore deleting the rows if item or store is deleted
    Column("item_id", ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("store_id", ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("item_id", "store_id", name="uq_item_store"),
)

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_at: Mapped[List["Store"]] = relationship(
        "Store",
        secondary=item_store,
        back_populates="items",
        passive_deletes=True
    )

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    orders: Mapped[List["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan", passive_deletes=True)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id",
                                                        ondelete="CASCADE"),
                                             index=True)
    price_eur: Mapped[Numeric] = mapped_column(Numeric(10,2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer: Mapped["Customer"] = relationship(back_populates="orders")

class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    items: Mapped[List["Item"]] = relationship(
        "Item",
        secondary=item_store,
        back_populates="available_at",
        passive_deletes=True
    )
