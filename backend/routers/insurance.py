from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter()

class InsuranceCreate(BaseModel):
    policy_name: str
    company: str
    premium_amount: float
    frequency: str
    due_date: str
    maturity_date: Optional[str] = None
    paid: bool = False

class InsuranceUpdate(BaseModel):
    policy_name: Optional[str] = None
    company: Optional[str] = None
    premium_amount: Optional[float] = None
    frequency: Optional[str] = None
    due_date: Optional[str] = None
    maturity_date: Optional[str] = None
    paid: Optional[bool] = None

@router.get("/")
def get_insurance():
    db = get_db()
    rows = db.execute("SELECT * FROM insurance ORDER BY due_date").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_insurance(ins: InsuranceCreate):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO insurance (policy_name, company, premium_amount, frequency, due_date, maturity_date, paid) VALUES (?,?,?,?,?,?,?)",
        (ins.policy_name, ins.company, ins.premium_amount, ins.frequency, ins.due_date, ins.maturity_date, int(ins.paid))
    )
    db.commit()
    row = db.execute("SELECT * FROM insurance WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return dict(row)

@router.put("/{ins_id}")
def update_insurance(ins_id: int, ins: InsuranceUpdate):
    db = get_db()
    existing = db.execute("SELECT * FROM insurance WHERE id=?", (ins_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Insurance not found")
    updates = {k: v for k, v in ins.model_dump().items() if v is not None}
    if 'paid' in updates:
        updates['paid'] = int(updates['paid'])
    sets = ", ".join(f"{k}=?" for k in updates)
    db.execute(f"UPDATE insurance SET {sets} WHERE id=?", (*updates.values(), ins_id))
    db.commit()
    row = db.execute("SELECT * FROM insurance WHERE id=?", (ins_id,)).fetchone()
    db.close()
    return dict(row)

@router.patch("/{ins_id}/toggle")
def toggle_insurance(ins_id: int):
    db = get_db()
    existing = db.execute("SELECT * FROM insurance WHERE id=?", (ins_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Insurance not found")
    db.execute("UPDATE insurance SET paid=1-paid WHERE id=?", (ins_id,))
    db.commit()
    row = db.execute("SELECT * FROM insurance WHERE id=?", (ins_id,)).fetchone()
    db.close()
    return dict(row)

@router.delete("/{ins_id}")
def delete_insurance(ins_id: int):
    db = get_db()
    db.execute("DELETE FROM insurance WHERE id=?", (ins_id,))
    db.commit()
    db.close()
    return {"deleted": True}
