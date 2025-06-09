#Financial Dashboard
import sys
import json
import requests 
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon 

api_key = "0IQO0B5TF7DXKK3H"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ticker_label = QLabel("Enter a stock ticker (like AAPL): ", self)
        self.ticker_input = QLineEdit(self)
        self.get_ticker = QPushButton("Enter", self)
        self.stock_price_label = QLabel(self)
        self.initUI()  

    def initUI(self):
        self.setWindowTitle("Financial Dashboard")
        self.setGeometry(400, 300, 300, 100)

        vbox = QVBoxLayout()
        vbox.addWidget(self.ticker_label)
        vbox.addWidget(self.ticker_input)
        vbox.addWidget(self.get_ticker)
        vbox.addWidget(self.stock_price_label)

        self.setLayout(vbox)
        
        self.ticker_label.setAlignment(Qt.AlignCenter)
        self.ticker_input.setAlignment(Qt.AlignCenter)
        self.stock_price_label.setAlignment(Qt.AlignCenter)

        self.ticker_label.setObjectName("ticker_label")
        self.ticker_input.setObjectName("ticker_input")
        self.get_ticker.setObjectName("get_ticker")
        self.stock_price_label.setObjectName("stock_price_label")

        self.setStyleSheet(""" 
            QLabel, QPushButton{
                font-family: courier new;           
                           }
            QLabel#ticker_label{
                font-size: 30px; 
                font-style: italic;
            }
            QLineEdit#ticker_input{
                font-size: 25px;
            }
            QPushButton#get_ticker{
                font-size: 25px;
                font-style: bold;               
            }
            QLabel#stock_price_label{
                font-size: 25px;               
            }
        """)
        
        self.get_ticker.clicked.connect(self.get_user_input)

    def get_user_input(self):
        symbol = self.ticker_input.text().strip().upper()
        
        if not symbol:
            self.display_error("Please enter a stock ticker")
            return
            
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    
        try:
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()
            
            if "Error Message" in data:
                self.display_error(f"Error: {data['Error Message']}")
                return
            
            if "Note" in data:
                self.display_error("API call frequency limit reached. Please try again later.")
                return
                
            if "Global Quote" not in data:
                self.display_error("Invalid ticker symbol or no data available")
                return
                
            self.display_stock_price(data)

        except requests.exceptions.RequestException as e:
            self.display_error(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            self.display_error("Error parsing API response")
        except Exception as e:
            self.display_error(f"An error occurred: {str(e)}")

    def display_error(self, message):
        self.stock_price_label.setText(message)
        self.stock_price_label.setStyleSheet("color: red;")

    def display_stock_price(self, data):
        try:
            stock_price_usd = float(data["Global Quote"]["05. price"])
            symbol = data["Global Quote"]["01. symbol"]
            
            self.stock_price_label.setStyleSheet("")
            
            self.stock_price_label.setText(f"{symbol}: ${stock_price_usd:.2f}")
            
        except (KeyError, ValueError) as e:
            self.display_error("Error processing stock price data")

def get_historical_prices(symbol, interval):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}min&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data

def current_stock_price(symbol):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

def get_balance_sheet(symbol):
    url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data 

def main():
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()
    sys.exit(app.exec_())

if __name__ =="__main__":
    main()