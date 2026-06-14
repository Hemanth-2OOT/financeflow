from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter()

class EMICreate(BaseModel):
    name: str
    bank: str
    amount: float
    interest_rate: float = 0
    due_date: str
    months_left: int = 0
    paid: bool = False

class EMIUpdate(BaseModel):
    name: Optional[str] = None
    bank: Optional[str] = None
    amount: Optional[float] = None
    interest_rate: Optional[float] = None
    due_date: Optional[str] = None
    months_left: Optional[int] = None
    paid: Optional[bool] = None

@router.get("/")
def get_emis():
    db = get_db()
    rows = db.execute("SELECT * FROM emis ORDER BY due_date").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_emi(emi: EMICreate):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO emis (name, bank, amount, interest_rate, due_date, months_left, paid) VALUES (?,?,?,?,?,?,?)",
        (emi.name, emi.bank, emi.amount, emi.interest_rate, emi.due_date, emi.months_left, int(emi.paid))
    )
    db.commit()
    row = db.execute("SELECT * FROM emis WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return dict(row)

@router.put("/{emi_id}")
def update_emi(emi_id: int, emi: EMIUpdate):
    db = get_db()
    existing = db.execute("SELECT * FROM emis WHERE id=?", (emi_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "EMI not found")
    updates = {k: v for k, v in emi.model_dump().items() if v is not None}
    if 'paid' in updates:
        updates['paid'] = int(updates['paid'])
    sets = ", ".join(f"{k}=?" for k in updates)
    db.execute(f"UPDATE emis SET {sets} WHERE id=?", (*updates.values(), emi_id))
    db.commit()
    row = db.execute("SELECT * FROM emis WHERE id=?", (emi_id,)).fetchone()
    db.close()
    return dict(row)

@router.patch("/{emi_id}/toggle")
def toggle_emi(emi_id: int):
    db = get_db()
    existing = db.execute("SELECT * FROM emis WHERE id=?", (emi_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "EMI not found")
    db.execute("UPDATE emis SET paid=1-paid WHERE id=?", (emi_id,))
    db.commit()
    row = db.execute("SELECT * FROM emis WHERE id=?", (emi_id,)).fetchone()
    db.close()
    return dict(row)

@router.delete("/{emi_id}")
def delete_emi(emi_id: int):
    db = get_db()
    db.execute("DELETE FROM emis WHERE id=?", (emi_id,))
    db.commit()
    db.close()
    return {"deleted": True}
