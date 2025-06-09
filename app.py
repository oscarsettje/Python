# Flask Currency Converter Web Application
from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

class ExchangeRatesAPI:
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.rates_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)
        
        self.supported_currencies = {
            'USD': 'US Dollar',
            'EUR': 'Euro', 
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'CHF': 'Swiss Franc',
            'AUD': 'Australian Dollar',
            'CAD': 'Canadian Dollar',
            'CNY': 'Chinese Yuan',
            'INR': 'Indian Rupee',
            'KRW': 'South Korean Won',
            'MXN': 'Mexican Peso',
            'BRL': 'Brazilian Real'
        }
    
    def fetch_rates(self, base_currency='USD'):
        try:
            response = requests.get(f"{self.base_url}{base_currency}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.rates_cache = data['rates']
            self.cache_timestamp = datetime.now()
            return True
            
        except Exception as e:
            print(f"API Error: {e}")
            return False
    
    def get_exchange_rate(self, currency, base='USD'):
        if (not self.rates_cache or 
            not self.cache_timestamp or 
            datetime.now() - self.cache_timestamp > self.cache_duration):
            
            if not self.fetch_rates(base):
                return self.get_fallback_rate(currency)
        
        return self.rates_cache.get(currency, 1.0)
    
    def get_fallback_rate(self, currency):
        fallback_rates = {
            'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CHF': 0.92,
            'AUD': 1.35, 'CAD': 1.25, 'CNY': 6.45, 'INR': 74.5, 
            'KRW': 1180.0, 'MXN': 20.5, 'BRL': 5.2
        }
        return fallback_rates.get(currency, 1.0)
    
    def get_all_rates(self):
        if not self.rates_cache:
            self.fetch_rates()
        return self.rates_cache
    
    def get_cache_info(self):
        if self.cache_timestamp:
            return {
                'last_updated': self.cache_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'age_minutes': int((datetime.now() - self.cache_timestamp).total_seconds() / 60)
            }
        return None

# Initialize the exchange rates API
fx_api = ExchangeRatesAPI()

def convert_currency(amount, input_currency, output_currency):
    if amount < 0:
        raise ValueError("Amount must be positive")
    
    if input_currency == output_currency:
        return amount
    
    if input_currency == 'USD':
        rate = fx_api.get_exchange_rate(output_currency)
        return amount * rate
    elif output_currency == 'USD':
        rate = fx_api.get_exchange_rate(input_currency)
        return amount / rate
    else:
        usd_rate = fx_api.get_exchange_rate(input_currency)
        target_rate = fx_api.get_exchange_rate(output_currency)
        return (amount / usd_rate) * target_rate

@app.route('/')
def index():
    return render_template('index.html', currencies=fx_api.supported_currencies)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        if amount < 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        converted_amount = convert_currency(amount, from_currency, to_currency)
        
        # Get the exchange rate used
        if from_currency == 'USD':
            rate = fx_api.get_exchange_rate(to_currency)
            rate_info = f"1 USD = {rate:.4f} {to_currency}"
        elif to_currency == 'USD':
            rate = fx_api.get_exchange_rate(from_currency)
            rate_info = f"1 {from_currency} = {1/rate:.4f} USD"
        else:
            usd_rate = fx_api.get_exchange_rate(from_currency)
            target_rate = fx_api.get_exchange_rate(to_currency)
            cross_rate = target_rate / usd_rate
            rate_info = f"1 {from_currency} = {cross_rate:.4f} {to_currency}"
        
        return jsonify({
            'converted_amount': round(converted_amount, 2),
            'rate_info': rate_info,
            'cache_info': fx_api.get_cache_info()
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Conversion failed'}), 500

@app.route('/rates')
def get_rates():
    try:
        rates = fx_api.get_all_rates()
        popular_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY', 'INR']
        
        popular_rates = {}
        for currency in popular_currencies:
            if currency in rates:
                popular_rates[currency] = {
                    'rate': rates[currency],
                    'name': fx_api.supported_currencies.get(currency, currency)
                }
        
        return jsonify({
            'rates': popular_rates,
            'cache_info': fx_api.get_cache_info()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch rates'}), 500

@app.route('/refresh', methods=['POST'])
def refresh_rates():
    try:
        success = fx_api.fetch_rates()
        if success:
            return jsonify({
                'message': 'Exchange rates refreshed successfully',
                'cache_info': fx_api.get_cache_info()
            })
        else:
            return jsonify({'error': 'Failed to refresh rates'}), 500
    except Exception as e:
        return jsonify({'error': 'Refresh failed'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='127.0.0.1', port=5000)