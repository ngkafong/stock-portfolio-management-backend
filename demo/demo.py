import requests
import json

base_url = "http://localhost:8000/"

headers = {
  'accept': 'application/json',
  'Content-Type': 'application/json'
}

if __name__ == '__main__':

  with open('portfolios.json') as f:
    portfolios = json.load(f)

  for portfolio in portfolios:
    r = requests.post(base_url+"portfolios", json=portfolio, headers=headers)
    try:
      print(r.json())
    except:
      print(r.status_code)

  with open('transactions.json') as f:
    transactions = json.load(f)

  for transaction in transactions:
    r = requests.post(base_url+"transactions", json=transaction, headers=headers)
    try:
      print(r.json())
    except:
      print(r.status_code)