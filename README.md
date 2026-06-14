# 🌊 FinanceFlow — Personal Finance Manager

A modern, dark-themed personal finance assistant to manage EMIs, life insurance premiums, gold loans, subscriptions, and bill reminders.

## Features

- **EMI Manager** — Track home loans, bike loans, personal loans, mobile EMIs
- **Insurance Tracker** — LIC, HDFC Life, SBI Life — monthly/quarterly/half-yearly/yearly premiums
- **Gold Loan Manager** — Auto-calculate monthly interest, track balance and due dates
- **Bills & Subscriptions** — Electricity, water, Netflix, Spotify, rent, internet
- **Smart Dashboard** — Total payable, overdue alerts, due-soon warnings, category breakdown
- **Analytics** — Interactive charts for EMI breakdown, expense distribution, bills, gold loans
- **Reminder System** — Red warnings for overdue, amber for due within 3 days

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS |
| Backend | Python Flask |
| Database | SQLite |
| Charts | Chart.js |
| Fonts | Sora + JetBrains Mono |

## Quick Start

### 1. Install dependencies
```bash
pip install Flask
```

### 2. Start the server
```bash
./start.sh
# or
cd backend && python3 main.py
```

### 3. Open in browser
```
http://localhost:8000
```

### 4. (Optional) Load sample data
```bash
cd backend && python3 seed.py
```

## Project Structure

```
financeflow/
├── backend/
│   ├── main.py          # Flask app + all API routes
│   ├── seed.py          # Sample data seeder
│   └── financeflow.db   # SQLite database (auto-created)
├── frontend/
│   └── index.html       # Complete SPA frontend
├── start.sh             # Startup script
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/emis/` | List all EMIs |
| POST | `/api/emis/` | Create EMI |
| PUT | `/api/emis/<id>` | Update EMI |
| PATCH | `/api/emis/<id>/toggle` | Toggle paid status |
| DELETE | `/api/emis/<id>` | Delete EMI |
| GET | `/api/insurance/` | List insurance policies |
| POST | `/api/insurance/` | Create policy |
| GET | `/api/gold-loans/` | List gold loans |
| POST | `/api/gold-loans/` | Create gold loan |
| GET | `/api/bills/` | List bills |
| POST | `/api/bills/` | Create bill |
| GET | `/api/dashboard/summary` | Dashboard stats & alerts |
| GET | `/api/dashboard/analytics` | Analytics data for charts |

## Database Schema

```sql
emis(id, name, bank, amount, interest_rate, due_date, months_left, paid)
insurance(id, policy_name, company, premium_amount, frequency, due_date, maturity_date, paid)
gold_loans(id, lender, gold_weight, loan_amount, interest_rate, monthly_interest, due_date, balance_amount, paid)
bills(id, name, amount, due_date, recurring, category, paid)
```
