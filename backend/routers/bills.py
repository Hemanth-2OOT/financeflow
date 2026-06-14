from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter()

class BillCreate(BaseModel):
    name: str
    amount: float
    due_date: str
    recurring: bool = True
    category: str = "other"
    paid: bool = False

class BillUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[str] = None
    recurring: Optional[bool] = None
    category: Optional[str] = None
    paid: Optional[bool] = None

@router.get("/")
def get_bills():
    db = get_db()
    rows = db.execute("SELECT * FROM bills ORDER BY due_date").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_bill(bill: BillCreate):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO bills (name, amount, due_date, recurring, category, paid) VALUES (?,?,?,?,?,?)",
        (bill.name, bill.amount, bill.due_date, int(bill.recurring), bill.category, int(bill.paid))
    )
    db.commit()
    row = db.execute("SELECT * FROM bills WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return dict(row)

@router.put("/{bill_id}")
def update_bill(bill_id: int, bill: BillUpdate):
    db = get_db()
    existing = db.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Bill not found")
    updates = {k: v for k, v in bill.model_dump().items() if v is not None}
    for key in ['paid', 'recurring']:
        if key in updates:
            updates[key] = int(updates[key])
    sets = ", ".join(f"{k}=?" for k in updates)
    db.execute(f"UPDATE bills SET {sets} WHERE id=?", (*updates.values(), bill_id))
    db.commit()
    row = db.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
    db.close()
    return dict(row)

@router.patch("/{bill_id}/toggle")
def toggle_bill(bill_id: int):
    db = get_db()
    existing = db.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Bill not found")
    db.execute("UPDATE bills SET paid=1-paid WHERE id=?", (bill_id,))
    db.commit()
    row = db.execute("SELECT * FROM bills WHERE id=?", (bill_id,)).fetchone()
    db.close()
    return dict(row)

@router.delete("/{bill_id}")
def delete_bill(bill_id: int):
    db = get_db()
    db.execute("DELETE FROM bills WHERE id=?", (bill_id,))
    db.commit()
    db.close()
    return {"deleted": True}
