# Schritt 1: Datenabruf
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime  # Fehlende Importanweisung hinzugefügt

def get_current_data(ticker_symbols): 
    # Fetch the current stock data
    stock_data = {}
    for symbol in ticker_symbols:
        ticker = yf.Ticker(symbol)
        current_data = ticker.info 
        stock_data[symbol] = { 
            "name": current_data.get("shortName", "Unbekannt"),
            "price": current_data.get("currentPrice", 0),
            "change": current_data.get("regularMarketChangePercent", 0),
            "market_cap": current_data.get("marketCap", 0),
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return stock_data

#Beispiele:
my_stocks = ["AAPL", "MSFT", "AMZN", "GOOGL"]

#Daten abrufen:
stock_data = get_current_data(my_stocks)
for symbol, data in stock_data.items():
    print(f"{data['name']} ({symbol}): {data['price']} EUR/USD, {data['change']}%, Market Cap: {data['market_cap']}")

#Schritt 2: Daten Visualisierung
def plot_current_prices(stock_data):
    #Aktuelle Preise als Balkendiagramm darstellen
    symbols = list(stock_data.keys())
    prices = [data["price"] for data in stock_data.values()]
    names = [data["name"] for data in stock_data.values()]
    
    #Farbcodierung für positive und negative Preisänderungen
    colors = ['green' if data["change"] >= 0 else 'red' for data in stock_data.values()]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(symbols, prices, color=colors)
    
    #Beschriftungen hinzufügen
    plt.title("Aktuelle Aktienkurse")
    plt.xlabel("Aktien")
    plt.ylabel("Preis (EUR/USD)")
    plt.xticks(rotation=45)
    
    # Werte über den Balken anzeigen
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

# Daten abrufen und visualisieren
stock_data = get_current_data(my_stocks)
plot_current_prices(stock_data)

# Schritt 3: Historische Daten abrufen und visualisieren
def get_historical_data(ticker_symbol, period="1mo"):
    # Historische Kursdaten abrufen
    ticker = yf.Ticker(ticker_symbol)
    hist_data = ticker.history(period=period)
    return hist_data

def plot_historical_data(ticker_symbol, period="1mo"):
    # Historische Kursdaten abrufen und visualisieren
    data = get_historical_data(ticker_symbol, period)
    
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label=f'{ticker_symbol} Schlusskurs')
    
    # Durschnittspreis hinzufügen 
    avg_price = data['Close'].mean()
    plt.axhline(avg_price, color='r', linestyle='--', label=f'Durchschnittspreis: {avg_price:.2f}')
    
    plt.title(f'{ticker_symbol} Kursverlauf ({period})')
    plt.xlabel('Datum')
    plt.ylabel('Preis (EUR/USD)')
    plt.legend()
    plt.tight_layout()
    plt.show()

# Beispiel:
plot_historical_data("AAPL", period="1mo")

#Schritt 4: Benachrichtigungssystem
def set_price_alert(ticker_symbol, target_price, is_above=True):  # Korrektur: "is above" zu "is_above"
    # Überprüft ob der aktuelle Preis den Zielpreis erreicht hat
    ticker = yf.Ticker(ticker_symbol)  # Einrückung korrigiert
    current_price = ticker.info.get("currentPrice", 0)
    if is_above:  # Einrückung korrigiert
        condition_met = current_price >= target_price
        direction = "über"
    else:
        condition_met = current_price <= target_price
        direction = "unter"
    if condition_met:
        print(f"ALARM: {ticker_symbol} ist jetzt bei {current_price:.2f}, "  # Leerzeichen in :.2f entfernt
              f"das ist {direction} deiner Schwelle von {target_price:.2f}!")  # Leerzeichen in :.2f entfernt
    return condition_met

# Beispiel:
set_price_alert("AAPL", 150, True)

# Schritt 5: Überwachung und Aktualisierung
import time
def monitor_stocks(ticker_symbols, check_interval=300, max_checks=None):
    # Überwacht die Aktienkurse in regelmäßigen Abständen
    checks = 0
    while max_checks is None or checks < max_checks:  # Einrückung korrigiert
        print(f"\n---Aktualisierung {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}---")  # datetime korrigiert

        stock_data = get_current_data(ticker_symbols)
        for symbol, data in stock_data.items():
            print(f"{data['name']} ({symbol}): {data['price']:.2f} EUR/USD, "  # Leerzeichen in :.2f entfernt
                  f"(Änderung: {data['change']:.2f}%)")  # Leerzeichen in :.2f entfernt und Klammer geschlossen
            
        checks += 1
        if max_checks is None or checks < max_checks:  # "None" korrigiert und Einrückung angepasst
            print(f"Nächste Aktualisierung in {check_interval // 60} Minuten...")
            time.sleep(check_interval)

#Schritt 6: Zusammenführung
def main():
    print("===AKTIEN-DATEN-TRACKER===")
    print("Was möchten Sie tun?")
    print("1. Aktuelle Kursdaten abrufen")
    print("2. Historische Daten visualisieren")
    print("3. Kursbenachrichtigung setzen")
    print("4. Aktienkurse überwachen")
    print("5. Beenden")
    choice = input("Bitte wählen Sie eine Option (1-5): ")  
    if choice == "1": 
        symbols = input("Geben Sie die Ticker-Symbole (kommagetrennt) ein: ").split(",")
        symbols = [s.strip() for s in symbols]
        stock_data = get_current_data(symbols)
        for symbol, data in stock_data.items():
            print(f"{data['name']} ({symbol}): {data['price']:.2f} EUR/USD, "  # Leerzeichen in :.2f entfernt
                  f"(Änderung: {data['change']:.2f}%)")  # Leerzeichen in :.2f entfernt und in eine Zeile zusammengefasst
        plot_current_prices(stock_data)
    elif choice == "2":
        symbol = input("Geben Sie das Ticker-Symbol ein: ").strip()
        period = input("Geben Sie den Zeitraum ein (z.B. 1mo, 3mo, 1y): ").strip()
        plot_historical_data(symbol, period)
    elif choice == "3":
        symbol = input("Geben Sie das Ticker-Symbol ein:").strip()
        price = float(input("Geben Sie den Zielpreis ein: "))
        direction = input("Benachrichtigung wenn Kurs über (o) oder unter der Schwelle: ")
        is_above = direction.startswith("o")
        set_price_alert(symbol, price, is_above)
    elif choice == "4":
        symbols = input("Geben Sie die Ticker-Symbole (kommagetrennt) ein: ").split(",")
        symbols = [s.strip() for s in symbols]
        interval = int(input("Geben Sie das Überwachungsintervall in Minuten ein: ")) * 60
        checks = input("Geben Sie die maximale Anzahl der Überprüfungen ein (0 für unendlich): ")  # Zu str geändert
        max_checks = int(checks) if checks and int(checks) > 0 else None  # Prüfung hinzugefügt
        monitor_stocks(symbols, interval, max_checks)
    elif choice == "5":
        print("Programm beendet.")
        return
    else:
        print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

if __name__ == "__main__":
    main()