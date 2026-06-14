import sqlite3, json, os
from flask import Flask, request, jsonify, send_from_directory
from datetime import date, timedelta

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "financeflow.db")
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS emis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, bank TEXT NOT NULL,
            amount REAL NOT NULL, interest_rate REAL DEFAULT 0,
            due_date TEXT NOT NULL, months_left INTEGER DEFAULT 0,
            paid INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS insurance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL, company TEXT NOT NULL,
            premium_amount REAL NOT NULL, frequency TEXT NOT NULL,
            due_date TEXT NOT NULL, maturity_date TEXT,
            paid INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS gold_loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lender TEXT NOT NULL, gold_weight REAL NOT NULL,
            loan_amount REAL NOT NULL, interest_rate REAL NOT NULL,
            monthly_interest REAL NOT NULL, due_date TEXT NOT NULL,
            balance_amount REAL NOT NULL, paid INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, amount REAL NOT NULL,
            due_date TEXT NOT NULL, recurring INTEGER DEFAULT 1,
            category TEXT DEFAULT 'other', paid INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit(); conn.close()

def row2dict(r): return dict(r) if r else None
def rows2list(rows): return [dict(r) for r in rows]

def days_until(s):
    try:
        d = date.fromisoformat(s)
        return (d - date.today()).days
    except: return 999

def cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@app.after_request
def add_cors(r): return cors(r)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'): return jsonify({'error':'not found'}), 404
    return send_from_directory(FRONTEND, 'index.html')

# ── EMIs ──────────────────────────────────────────────────────────────────────
@app.route('/api/emis/', methods=['GET','OPTIONS'])
def get_emis():
    db = get_db()
    rows = rows2list(db.execute("SELECT * FROM emis ORDER BY due_date").fetchall())
    db.close(); return jsonify(rows)

@app.route('/api/emis/', methods=['POST'])
def create_emi():
    d = request.json
    db = get_db()
    cur = db.execute("INSERT INTO emis(name,bank,amount,interest_rate,due_date,months_left,paid) VALUES(?,?,?,?,?,?,?)",
        (d['name'],d['bank'],d['amount'],d.get('interest_rate',0),d['due_date'],d.get('months_left',0),int(d.get('paid',False))))
    db.commit()
    row = row2dict(db.execute("SELECT * FROM emis WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(row), 201

@app.route('/api/emis/<int:eid>', methods=['PUT','OPTIONS'])
def update_emi(eid):
    d = request.json
    db = get_db()
    fields = ['name','bank','amount','interest_rate','due_date','months_left']
    sets = ','.join(f"{f}=?" for f in fields)
    vals = [d.get(f) for f in fields] + [eid]
    db.execute(f"UPDATE emis SET {sets} WHERE id=?", vals)
    db.commit()
    row = row2dict(db.execute("SELECT * FROM emis WHERE id=?",(eid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/emis/<int:eid>/toggle', methods=['PATCH','OPTIONS'])
def toggle_emi(eid):
    db = get_db()
    db.execute("UPDATE emis SET paid=1-paid WHERE id=?",(eid,)); db.commit()
    row = row2dict(db.execute("SELECT * FROM emis WHERE id=?",(eid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/emis/<int:eid>', methods=['DELETE'])
def delete_emi(eid):
    db = get_db(); db.execute("DELETE FROM emis WHERE id=?",(eid,)); db.commit(); db.close()
    return jsonify({'deleted':True})

# ── Insurance ─────────────────────────────────────────────────────────────────
@app.route('/api/insurance/', methods=['GET','OPTIONS'])
def get_insurance():
    db = get_db()
    rows = rows2list(db.execute("SELECT * FROM insurance ORDER BY due_date").fetchall())
    db.close(); return jsonify(rows)

@app.route('/api/insurance/', methods=['POST'])
def create_insurance():
    d = request.json; db = get_db()
    cur = db.execute("INSERT INTO insurance(policy_name,company,premium_amount,frequency,due_date,maturity_date,paid) VALUES(?,?,?,?,?,?,?)",
        (d['policy_name'],d['company'],d['premium_amount'],d['frequency'],d['due_date'],d.get('maturity_date'),0))
    db.commit()
    row = row2dict(db.execute("SELECT * FROM insurance WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(row), 201

@app.route('/api/insurance/<int:iid>', methods=['PUT','OPTIONS'])
def update_insurance(iid):
    d = request.json; db = get_db()
    fields = ['policy_name','company','premium_amount','frequency','due_date','maturity_date']
    sets = ','.join(f"{f}=?" for f in fields)
    db.execute(f"UPDATE insurance SET {sets} WHERE id=?", [d.get(f) for f in fields]+[iid])
    db.commit()
    row = row2dict(db.execute("SELECT * FROM insurance WHERE id=?",(iid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/insurance/<int:iid>/toggle', methods=['PATCH','OPTIONS'])
def toggle_insurance(iid):
    db = get_db()
    db.execute("UPDATE insurance SET paid=1-paid WHERE id=?",(iid,)); db.commit()
    row = row2dict(db.execute("SELECT * FROM insurance WHERE id=?",(iid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/insurance/<int:iid>', methods=['DELETE'])
def delete_insurance(iid):
    db = get_db(); db.execute("DELETE FROM insurance WHERE id=?",(iid,)); db.commit(); db.close()
    return jsonify({'deleted':True})

# ── Gold Loans ────────────────────────────────────────────────────────────────
@app.route('/api/gold-loans/', methods=['GET','OPTIONS'])
def get_gold():
    db = get_db()
    rows = rows2list(db.execute("SELECT * FROM gold_loans ORDER BY due_date").fetchall())
    db.close(); return jsonify(rows)

@app.route('/api/gold-loans/', methods=['POST'])
def create_gold():
    d = request.json; db = get_db()
    cur = db.execute("INSERT INTO gold_loans(lender,gold_weight,loan_amount,interest_rate,monthly_interest,due_date,balance_amount,paid) VALUES(?,?,?,?,?,?,?,?)",
        (d['lender'],d['gold_weight'],d['loan_amount'],d['interest_rate'],d['monthly_interest'],d['due_date'],d['balance_amount'],0))
    db.commit()
    row = row2dict(db.execute("SELECT * FROM gold_loans WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(row), 201

@app.route('/api/gold-loans/<int:gid>', methods=['PUT','OPTIONS'])
def update_gold(gid):
    d = request.json; db = get_db()
    fields = ['lender','gold_weight','loan_amount','interest_rate','monthly_interest','due_date','balance_amount']
    sets = ','.join(f"{f}=?" for f in fields)
    db.execute(f"UPDATE gold_loans SET {sets} WHERE id=?", [d.get(f) for f in fields]+[gid])
    db.commit()
    row = row2dict(db.execute("SELECT * FROM gold_loans WHERE id=?",(gid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/gold-loans/<int:gid>/toggle', methods=['PATCH','OPTIONS'])
def toggle_gold(gid):
    db = get_db()
    db.execute("UPDATE gold_loans SET paid=1-paid WHERE id=?",(gid,)); db.commit()
    row = row2dict(db.execute("SELECT * FROM gold_loans WHERE id=?",(gid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/gold-loans/<int:gid>', methods=['DELETE'])
def delete_gold(gid):
    db = get_db(); db.execute("DELETE FROM gold_loans WHERE id=?",(gid,)); db.commit(); db.close()
    return jsonify({'deleted':True})

# ── Bills ─────────────────────────────────────────────────────────────────────
@app.route('/api/bills/', methods=['GET','OPTIONS'])
def get_bills():
    db = get_db()
    rows = rows2list(db.execute("SELECT * FROM bills ORDER BY due_date").fetchall())
    db.close(); return jsonify(rows)

@app.route('/api/bills/', methods=['POST'])
def create_bill():
    d = request.json; db = get_db()
    cur = db.execute("INSERT INTO bills(name,amount,due_date,recurring,category,paid) VALUES(?,?,?,?,?,?)",
        (d['name'],d['amount'],d['due_date'],int(d.get('recurring',True)),d.get('category','other'),0))
    db.commit()
    row = row2dict(db.execute("SELECT * FROM bills WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(row), 201

@app.route('/api/bills/<int:bid>', methods=['PUT','OPTIONS'])
def update_bill(bid):
    d = request.json; db = get_db()
    fields = ['name','amount','due_date','category']
    sets = ','.join(f"{f}=?" for f in fields)
    db.execute(f"UPDATE bills SET {sets} WHERE id=?", [d.get(f) for f in fields]+[bid])
    db.commit()
    row = row2dict(db.execute("SELECT * FROM bills WHERE id=?",(bid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/bills/<int:bid>/toggle', methods=['PATCH','OPTIONS'])
def toggle_bill(bid):
    db = get_db()
    db.execute("UPDATE bills SET paid=1-paid WHERE id=?",(bid,)); db.commit()
    row = row2dict(db.execute("SELECT * FROM bills WHERE id=?",(bid,)).fetchone())
    db.close(); return jsonify(row)

@app.route('/api/bills/<int:bid>', methods=['DELETE'])
def delete_bill(bid):
    db = get_db(); db.execute("DELETE FROM bills WHERE id=?",(bid,)); db.commit(); db.close()
    return jsonify({'deleted':True})

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route('/api/dashboard/summary', methods=['GET','OPTIONS'])
def dashboard_summary():
    db = get_db()
    emis = rows2list(db.execute("SELECT * FROM emis").fetchall())
    ins = rows2list(db.execute("SELECT * FROM insurance").fetchall())
    golds = rows2list(db.execute("SELECT * FROM gold_loans").fetchall())
    bills = rows2list(db.execute("SELECT * FROM bills").fetchall())
    db.close()

    all_items = []
    for e in emis:
        e['_type']='EMI'; e['_days']=days_until(e['due_date']); all_items.append(e)
    for i in ins:
        i['_type']='Insurance'; i['_days']=days_until(i['due_date']); all_items.append(i)
    for g in golds:
        g['_type']='Gold Loan'; g['_days']=days_until(g['due_date']); all_items.append(g)
    for b in bills:
        b['_type']='Bill'; b['_days']=days_until(b['due_date']); all_items.append(b)

    overdue = [x for x in all_items if x['_days'] < 0 and not x.get('paid')]
    due_soon = [x for x in all_items if 0 <= x['_days'] <= 3 and not x.get('paid')]
    upcoming = sorted([x for x in all_items if 4 <= x['_days'] <= 30 and not x.get('paid')], key=lambda x: x['_days'])[:5]

    te = sum(e['amount'] for e in emis)
    ti = sum(i['premium_amount'] for i in ins)
    tg = sum(g['monthly_interest'] for g in golds)
    tb = sum(b['amount'] for b in bills)
    total = te+ti+tg+tb
    unpaid = sum(e['amount'] for e in emis if not e['paid']) + sum(i['premium_amount'] for i in ins if not i['paid']) + sum(g['monthly_interest'] for g in golds if not g['paid']) + sum(b['amount'] for b in bills if not b['paid'])

    return jsonify({
        'total_monthly': round(total,2), 'total_unpaid': round(unpaid,2), 'total_paid': round(total-unpaid,2),
        'emi_total': round(te,2), 'insurance_total': round(ti,2), 'gold_total': round(tg,2), 'bills_total': round(tb,2),
        'overdue_count': len(overdue), 'due_soon_count': len(due_soon),
        'overdue_items': overdue[:5], 'due_soon_items': due_soon[:5], 'upcoming_items': upcoming,
        'category_breakdown': {'EMIs': round(te,2), 'Insurance': round(ti,2), 'Gold Loans': round(tg,2), 'Bills': round(tb,2)}
    })

@app.route('/api/dashboard/analytics', methods=['GET','OPTIONS'])
def dashboard_analytics():
    db = get_db()
    emis = rows2list(db.execute("SELECT * FROM emis").fetchall())
    ins = rows2list(db.execute("SELECT * FROM insurance").fetchall())
    golds = rows2list(db.execute("SELECT * FROM gold_loans").fetchall())
    bills = rows2list(db.execute("SELECT * FROM bills").fetchall())
    db.close()
    return jsonify({
        'emi_breakdown': [{'name':e['name'],'amount':e['amount']} for e in emis],
        'bill_breakdown': [{'name':b['name'],'amount':b['amount']} for b in bills],
        'gold_breakdown': [{'lender':g['lender'],'loan_amount':g['loan_amount'],'monthly_interest':g['monthly_interest']} for g in golds],
        'insurance_breakdown': [{'policy':i['policy_name'],'premium':i['premium_amount']} for i in ins],
        'totals': {'emis': sum(e['amount'] for e in emis), 'insurance': sum(i['premium_amount'] for i in ins), 'gold': sum(g['monthly_interest'] for g in golds), 'bills': sum(b['amount'] for b in bills)}
    })

if __name__ == '__main__':
    init_db()
    print("\n🌊  FinanceFlow is running!")
    print("   ➜  Open: http://localhost:8000")
    print("   Press Ctrl+C to stop.\n")
    app.run(host='0.0.0.0', port=8000, debug=True)
