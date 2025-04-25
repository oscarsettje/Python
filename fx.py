# Currency converter
base_currency = input("Choose a currency (USD; EUR, GBP, JPY, CHF, AUD, CAD): ")
amount = float(input("Enter the amount: "))
target_currency = input("Enter the target currency (USD; EUR, GBP, JPY, CHF, AUD, CAD): ")
USD = 1
EUR = 0.88
GBP = 0.75
JPY = 143.50
CHF = 0.83
AUD = 1.53
CAD = 1.39
if base_currency == "USD":
    amount = amount / USD
elif base_currency == "EUR":
    amount = amount / EUR
elif base_currency == "GBP":
    amount = amount / GBP
elif base_currency == "JPY":
    amount = amount / JPY
elif base_currency == "CHF":
    amount = amount / CHF
elif base_currency == "AUD":
    amount = amount / AUD
elif base_currency == "CAD":
    amount = amount / CAD
if target_currency == "USD":
    amount = amount * USD   
elif target_currency == "EUR":  
    amount = amount * EUR
elif target_currency == "GBP":
    amount = amount * GBP
elif target_currency == "JPY":
    amount = amount * JPY
elif target_currency == "CHF": 
    amount = amount * CHF
elif target_currency == "AUD":
    amount = amount * AUD
elif target_currency == "CAD":
    amount = amount * CAD
if amount < 0:
    print("Invalid amount")
else: 
    print(f"{amount} {target_currency}")