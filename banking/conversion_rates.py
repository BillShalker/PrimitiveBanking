import requests
from django.core.cache import cache

def currency_rates():
    cached_rates = cache.get('conversion_rates')
    if cached_rates:
        return cached_rates
    else:
        # Wysyłanie zapytania do API i pobieranie kursów walut
        response = requests.get('https://v6.exchangerate-api.com/v6/777b1dc3d0dd56ec87f21cc0/latest/USD')
        if response.status_code == 200:  # Sprawdzanie, czy żądanie zakończyło się sukcesem
            rates = response.json().get('conversion_rates')
            if rates:
                cache.set('conversion_rates', rates, 60*60)  # Zapisywanie kursów w cache na 1 godzinę
                return rates
        return None  # Zwracanie None, jeśli nie uda się pobrać kursów walut


