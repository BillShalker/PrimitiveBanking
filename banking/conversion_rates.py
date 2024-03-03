import requests


def currency_rates():
    page = requests.get('https://v6.exchangerate-api.com/v6/777b1dc3d0dd56ec87f21cc0/latest/USD')
    return page.json()['conversion_rates']
