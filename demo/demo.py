import requests
import json
import os

base_url = "http://23.94.100.114/"

headers = {
  'accept': 'application/json',
  'Content-Type': 'application/json'
}

if __name__ == '__main__':

  script_dir = os.path.dirname(__file__)

  with open(script_dir+'/portfolios.json') as f:
    portfolios = json.load(f)

  for portfolio in portfolios:
    r = requests.post(base_url+"portfolios", json=portfolio, headers=headers)
    try:
      print(r.json())
    except:
      print(r.status_code)

  with open(script_dir+'/transactions.json') as f:
    transactions = json.load(f)

  for transaction in transactions:
    r = requests.post(base_url+"transactions", json=transaction, headers=headers)
    try:
      print(r.json())
    except:
      print(r.status_code)