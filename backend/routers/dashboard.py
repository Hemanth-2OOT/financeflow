from fastapi import APIRouter
from database import get_db
from datetime import date, timedelta

router = APIRouter()

def days_until(due_date_str):
    try:
        due = date.fromisoformat(due_date_str)
        return (due - date.today()).days
    except:
        return 999

@router.get("/summary")
def get_dashboard_summary():
    db = get_db()
    today = date.today()
    month_end = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    emis = [dict(r) for r in db.execute("SELECT * FROM emis").fetchall()]
    insurance = [dict(r) for r in db.execute("SELECT * FROM insurance").fetchall()]
    gold_loans = [dict(r) for r in db.execute("SELECT * FROM gold_loans").fetchall()]
    bills = [dict(r) for r in db.execute("SELECT * FROM bills").fetchall()]
    db.close()

    total_emis = sum(e['amount'] for e in emis)
    unpaid_emis = sum(e['amount'] for e in emis if not e['paid'])
    paid_emis = sum(e['amount'] for e in emis if e['paid'])

    total_insurance = sum(i['premium_amount'] for i in insurance)
    unpaid_insurance = sum(i['premium_amount'] for i in insurance if not i['paid'])

    total_gold = sum(g['monthly_interest'] for g in gold_loans)
    unpaid_gold = sum(g['monthly_interest'] for g in gold_loans if not g['paid'])

    total_bills = sum(b['amount'] for b in bills)
    unpaid_bills = sum(b['amount'] for b in bills if not b['paid'])

    total_monthly = total_emis + total_insurance + total_gold + total_bills
    total_unpaid = unpaid_emis + unpaid_insurance + unpaid_gold + unpaid_bills

    all_items = []
    for e in emis:
        d = days_until(e['due_date'])
        e['_type'] = 'EMI'
        e['_days'] = d
        all_items.append(e)
    for i in insurance:
        d = days_until(i['due_date'])
        i['_type'] = 'Insurance'
        i['_days'] = d
        all_items.append(i)
    for g in gold_loans:
        d = days_until(g['due_date'])
        g['_type'] = 'Gold Loan'
        g['_days'] = d
        all_items.append(g)
    for b in bills:
        d = days_until(b['due_date'])
        b['_type'] = 'Bill'
        b['_days'] = d
        all_items.append(b)

    overdue = [x for x in all_items if x['_days'] < 0 and not x.get('paid')]
    due_soon = [x for x in all_items if 0 <= x['_days'] <= 3 and not x.get('paid')]
    upcoming = sorted([x for x in all_items if 4 <= x['_days'] <= 30 and not x.get('paid')], key=lambda x: x['_days'])[:5]

    return {
        "total_monthly": round(total_monthly, 2),
        "total_unpaid": round(total_unpaid, 2),
        "total_paid": round(total_monthly - total_unpaid, 2),
        "emi_total": round(total_emis, 2),
        "insurance_total": round(total_insurance, 2),
        "gold_total": round(total_gold, 2),
        "bills_total": round(total_bills, 2),
        "overdue_count": len(overdue),
        "due_soon_count": len(due_soon),
        "overdue_items": overdue[:5],
        "due_soon_items": due_soon[:5],
        "upcoming_items": upcoming,
        "category_breakdown": {
            "EMIs": round(total_emis, 2),
            "Insurance": round(total_insurance, 2),
            "Gold Loans": round(total_gold, 2),
            "Bills": round(total_bills, 2),
        }
    }

@router.get("/analytics")
def get_analytics():
    db = get_db()
    emis = [dict(r) for r in db.execute("SELECT * FROM emis").fetchall()]
    insurance = [dict(r) for r in db.execute("SELECT * FROM insurance").fetchall()]
    gold_loans = [dict(r) for r in db.execute("SELECT * FROM gold_loans").fetchall()]
    bills = [dict(r) for r in db.execute("SELECT * FROM bills").fetchall()]
    db.close()

    emi_breakdown = [{"name": e['name'], "amount": e['amount'], "bank": e['bank']} for e in emis]
    bill_breakdown = [{"name": b['name'], "amount": b['amount'], "category": b['category']} for b in bills]
    gold_breakdown = [{"lender": g['lender'], "loan_amount": g['loan_amount'], "monthly_interest": g['monthly_interest']} for g in gold_loans]
    ins_breakdown = [{"policy": i['policy_name'], "premium": i['premium_amount'], "frequency": i['frequency']} for i in insurance]

    return {
        "emi_breakdown": emi_breakdown,
        "bill_breakdown": bill_breakdown,
        "gold_breakdown": gold_breakdown,
        "insurance_breakdown": ins_breakdown,
        "totals": {
            "emis": sum(e['amount'] for e in emis),
            "insurance": sum(i['premium_amount'] for i in insurance),
            "gold": sum(g['monthly_interest'] for g in gold_loans),
            "bills": sum(b['amount'] for b in bills),
        }
    }
