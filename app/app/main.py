from __future__ import annotations
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

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