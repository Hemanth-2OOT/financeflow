from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db

router = APIRouter()

class GoldLoanCreate(BaseModel):
    lender: str
    gold_weight: float
    loan_amount: float
    interest_rate: float
    monthly_interest: float
    due_date: str
    balance_amount: float
    paid: bool = False

class GoldLoanUpdate(BaseModel):
    lender: Optional[str] = None
    gold_weight: Optional[float] = None
    loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    monthly_interest: Optional[float] = None
    due_date: Optional[str] = None
    balance_amount: Optional[float] = None
    paid: Optional[bool] = None

@router.get("/")
def get_gold_loans():
    db = get_db()
    rows = db.execute("SELECT * FROM gold_loans ORDER BY due_date").fetchall()
    db.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_gold_loan(loan: GoldLoanCreate):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO gold_loans (lender, gold_weight, loan_amount, interest_rate, monthly_interest, due_date, balance_amount, paid) VALUES (?,?,?,?,?,?,?,?)",
        (loan.lender, loan.gold_weight, loan.loan_amount, loan.interest_rate, loan.monthly_interest, loan.due_date, loan.balance_amount, int(loan.paid))
    )
    db.commit()
    row = db.execute("SELECT * FROM gold_loans WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return dict(row)

@router.put("/{loan_id}")
def update_gold_loan(loan_id: int, loan: GoldLoanUpdate):
    db = get_db()
    existing = db.execute("SELECT * FROM gold_loans WHERE id=?", (loan_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Gold loan not found")
    updates = {k: v for k, v in loan.model_dump().items() if v is not None}
    if 'paid' in updates:
        updates['paid'] = int(updates['paid'])
    sets = ", ".join(f"{k}=?" for k in updates)
    db.execute(f"UPDATE gold_loans SET {sets} WHERE id=?", (*updates.values(), loan_id))
    db.commit()
    row = db.execute("SELECT * FROM gold_loans WHERE id=?", (loan_id,)).fetchone()
    db.close()
    return dict(row)

@router.patch("/{loan_id}/toggle")
def toggle_gold_loan(loan_id: int):
    db = get_db()
    existing = db.execute("SELECT * FROM gold_loans WHERE id=?", (loan_id,)).fetchone()
    if not existing:
        raise HTTPException(404, "Gold loan not found")
    db.execute("UPDATE gold_loans SET paid=1-paid WHERE id=?", (loan_id,))
    db.commit()
    row = db.execute("SELECT * FROM gold_loans WHERE id=?", (loan_id,)).fetchone()
    db.close()
    return dict(row)

@router.delete("/{loan_id}")
def delete_gold_loan(loan_id: int):
    db = get_db()
    db.execute("DELETE FROM gold_loans WHERE id=?", (loan_id,))
    db.commit()
    db.close()
    return {"deleted": True}
