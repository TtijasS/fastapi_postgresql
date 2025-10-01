from __future__ import annotations

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from .database import get_db

app = FastAPI(title="FastAPI + Postgres Template")

@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}

@app.post("/items", response_model=schemas.ItemRead, tags=["items"])
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = models.Item(name=payload.name, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/items", response_model=list[schemas.ItemRead], tags=["items"])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).order_by(models.Item.id.desc()).all()

@app.post("/customers", response_model=schemas.CustomerRead, tags=["customers"])
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = models.Customer(**payload.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(customer)
    return customer

@app.get("/customers", response_model=list[schemas.CustomerRead], tags=["customers"])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).order_by(models.Customer.id.desc()).all()

@app.get("/customers/{customer_id}", response_model=schemas.CustomerRead, tags=["customers"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c

@app.patch("/customers/{customer_id}", response_model=schemas.CustomerRead, tags=["customers"])
def update_customer(customer_id: int, payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    c = db.get(models.Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(c)
    return c

@app.delete("/customers/{customer_id}", status_code=204, tags=["customers"])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c)
    db.commit()
    return None

@app.post("/orders", response_model=schemas.OrderRead, tags=["orders"])
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    customer = db.get(models.Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail=f"Customer '{payload.customer_id}' not found")
    
    order = models.Order(**payload.model_dump())
    db.add(order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to commit the db with new order")
    db.refresh(order)

    return order

@app.get("/orders", response_model=list[schemas.OrderRead], tags=["orders"])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).order_by(models.Order.id.desc()).all()

@app.post("/stores", response_model=schemas.StoreRead, tags=["stores"])
def create_store(payload: schemas.StoreCreate, db: Session = Depends(get_db)):
    store = models.Store(name=payload.name, location=payload.location)

    if payload.item_ids:
        items = db.query(models.Item).filter(models.Item.id.in_(payload.item_ids)).all()
        if len(items) != len(set(payload.item_ids)):
            missing = set(payload.item_ids) - {i.id for i in items}
            raise HTTPException(status_code=400, detail=f"Unknown item ids: {sorted(missing)}")
        store.items = items

    db.add(store)
    db.commit()
    db.refresh(store)
    return store

@app.get("/stores", response_model=list[schemas.StoreRead], tags=["stores"])
def list_stores(db: Session = Depends(get_db)):
    return (
        db.query(models.Store).options(joinedload(models.Store.items)).order_by(models.Store.id.desc()).all()
    )

@app.get("/stores/{store_id}", response_model=schemas.StoreRead, tags=["stores"])
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = (
        db.query(models.Store).options(joinedload(models.Store.items)).filter(models.Store.id == store_id).first()
    )
    if not store:
        raise HTTPException(status_code=404, detail="Not found")
    return store

@app.put("/stores/{store_id}/items", response_model=schemas.StoreRead, tags=["stores"])
def set_store_items(store_id: int, payload: schemas.StoreItemsUpdate, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Not found")

    items = db.query(models.Item).filter(models.Item.id.in_(payload.item_ids)).all()
    if len(items) != len(set(payload.item_ids)):
        missing = set(payload.item_ids) - {i.id for i in items}
        raise HTTPException(status_code=400, detail=f"Unknown item ids: {sorted(missing)}")

    store.items = items
    db.commit()
    db.refresh(store)
    return store

@app.delete("/stores/{store_id}", status_code=204, tags=["stores"])
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(store)
    db.commit()
    return None