"""Seed FinanceFlow with sample data for demo purposes."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import main

main.init_db()
app = main.app

with app.test_client() as c:
    # EMIs
    c.post('/api/emis/', json={'name':'Home Loan','bank':'SBI','amount':28500,'interest_rate':8.5,'due_date':'2026-06-20','months_left':168})
    c.post('/api/emis/', json={'name':'Bike Loan','bank':'HDFC','amount':4200,'interest_rate':11.5,'due_date':'2026-06-15','months_left':24})
    c.post('/api/emis/', json={'name':'Mobile EMI','bank':'Bajaj Finance','amount':1800,'interest_rate':0,'due_date':'2026-06-05','months_left':6})
    c.post('/api/emis/', json={'name':'Personal Loan','bank':'ICICI','amount':7500,'interest_rate':14.5,'due_date':'2026-06-12','months_left':18})

    # Insurance
    c.post('/api/insurance/', json={'policy_name':'Term Life Plan','company':'LIC','premium_amount':12000,'frequency':'yearly','due_date':'2026-07-01','maturity_date':'2045-07-01'})
    c.post('/api/insurance/', json={'policy_name':'Health Shield','company':'HDFC Life','premium_amount':3500,'frequency':'quarterly','due_date':'2026-06-30','maturity_date':'2040-06-30'})
    c.post('/api/insurance/', json={'policy_name':'Endowment Plan','company':'SBI Life','premium_amount':8000,'frequency':'half-yearly','due_date':'2026-09-15','maturity_date':'2038-09-15'})

    # Gold Loans
    c.post('/api/gold-loans/', json={'lender':'Muthoot Finance','gold_weight':25.5,'loan_amount':120000,'interest_rate':12,'monthly_interest':1200,'due_date':'2026-06-25','balance_amount':120000})
    c.post('/api/gold-loans/', json={'lender':'Manappuram Gold','gold_weight':15.0,'loan_amount':72000,'interest_rate':13.5,'monthly_interest':810,'due_date':'2026-07-10','balance_amount':72000})

    # Bills
    c.post('/api/bills/', json={'name':'Electricity','amount':1850,'due_date':'2026-06-18','recurring':True,'category':'utility'})
    c.post('/api/bills/', json={'name':'Internet (Jio Fiber)','amount':999,'due_date':'2026-06-22','recurring':True,'category':'internet'})
    c.post('/api/bills/', json={'name':'Water Bill','amount':350,'due_date':'2026-06-28','recurring':True,'category':'utility'})
    c.post('/api/bills/', json={'name':'Netflix','amount':649,'due_date':'2026-06-14','recurring':True,'category':'subscription'})
    c.post('/api/bills/', json={'name':'Spotify','amount':119,'due_date':'2026-06-10','recurring':True,'category':'subscription'})
    c.post('/api/bills/', json={'name':'House Rent','amount':18000,'due_date':'2026-06-01','recurring':True,'category':'rent'})

    # Mark a few as paid
    c.patch('/api/emis/3/toggle')  # Mobile EMI paid
    c.patch('/api/bills/6/toggle')  # Rent paid

print("✅ Sample data seeded successfully!")
