import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import sqlite3
import os

# Datenbankfunktionen
def initialize_database():
    """Datenbank erstellen und notwendige Tabellen initialisieren"""
    # Prüfen, ob Datenbankdatei bereits existiert
    db_exists = os.path.isfile('stocktracker.db')
    
    # Verbindung zur Datenbank herstellen (wird erstellt, falls nicht vorhanden)
    conn = sqlite3.connect('stocktracker.db')
    cursor = conn.cursor()
    
    # Tabellen erstellen, falls sie noch nicht existieren
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        change_percent REAL,
        market_cap REAL,
        timestamp DATETIME NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        date DATETIME NOT NULL,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        volume INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        target_price REAL NOT NULL,
        is_above BOOLEAN NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL
    )
    ''')
    
    conn.commit()
    
    if not db_exists:
        print("Datenbank wurde erfolgreich erstellt.")
    
    return conn

def save_current_data(conn, stock_data):
    """Aktuelle Aktiendaten in der Datenbank speichern"""
    cursor = conn.cursor()
    
    for symbol, data in stock_data.items():
        cursor.execute('''
        INSERT INTO stock_prices (symbol, price, change_percent, market_cap, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            symbol,
            data['price'],
            data['change'],
            data['market_cap'],
            data['timestamp']
        ))
    
    conn.commit()
    print(f"{len(stock_data)} Datensätze in die Datenbank gespeichert.")

def save_historical_data(conn, symbol, hist_data):
    """Historische Aktiendaten in der Datenbank speichern"""
    cursor = conn.cursor()
    
    # Existierende Daten für das Symbol löschen, um Duplikate zu vermeiden
    cursor.execute('DELETE FROM stock_history WHERE symbol = ?', (symbol,))
    
    # Neue Daten einfügen
    for date, row in hist_data.iterrows():
        cursor.execute('''
        INSERT INTO stock_history (symbol, date, open_price, high_price, low_price, close_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            date.strftime('%Y-%m-%d'),
            row['Open'],
            row['High'],
            row['Low'],
            row['Close'],
            row['Volume'] if 'Volume' in row else 0
        ))
    
    conn.commit()
    print(f"{len(hist_data)} historische Datensätze für {symbol} gespeichert.")

def save_alert(conn, symbol, target_price, is_above):
    """Preisalarm in der Datenbank speichern"""
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO alerts (symbol, target_price, is_above, created_at)
    VALUES (?, ?, ?, ?)
    ''', (
        symbol,
        target_price,
        is_above,
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    print(f"Preisalarm für {symbol} bei {target_price} gespeichert.")

def get_saved_alerts(conn):
    """Alle aktiven Preisalarme aus der Datenbank abrufen"""
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, symbol, target_price, is_above FROM alerts WHERE is_active = 1')
    alerts = cursor.fetchall()
    
    return alerts

def get_price_history(conn, symbol, limit=30):
    """Preishistorie für ein Symbol aus der Datenbank abrufen"""
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT date, close_price 
    FROM stock_history 
    WHERE symbol = ? 
    ORDER BY date DESC 
    LIMIT ?
    ''', (symbol, limit))
    
    history = cursor.fetchall()
    
    return history

def get_latest_prices(conn, symbols=None):
    """Aktuelle Preise aus der Datenbank abrufen"""
    cursor = conn.cursor()
    
    if symbols:
        placeholders = ', '.join(['?' for _ in symbols])
        cursor.execute(f'''
        SELECT symbol, MAX(timestamp), price, change_percent
        FROM stock_prices
        WHERE symbol IN ({placeholders})
        GROUP BY symbol
        ''', symbols)
    else:
        cursor.execute('''
        SELECT symbol, MAX(timestamp), price, change_percent
        FROM stock_prices
        GROUP BY symbol
        ''')
    
    latest_prices = cursor.fetchall()
    
    return latest_prices

# Bestehende Funktionen mit Datenbankunterstützung

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
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return stock_data

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

def get_historical_data(ticker_symbol, period="1mo"):
    # Historische Kursdaten abrufen
    ticker = yf.Ticker(ticker_symbol)
    hist_data = ticker.history(period=period)
    return hist_data

def plot_historical_data(ticker_symbol, period="1mo", conn=None):
    # Historische Kursdaten abrufen und visualisieren
    data = get_historical_data(ticker_symbol, period)
    
    # Wenn Datenbankverbindung übergeben wurde, Daten speichern
    if conn:
        save_historical_data(conn, ticker_symbol, data)
    
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

def set_price_alert(ticker_symbol, target_price, is_above=True, conn=None):
    # Überprüft ob der aktuelle Preis den Zielpreis erreicht hat
    ticker = yf.Ticker(ticker_symbol)
    current_price = ticker.info.get("currentPrice", 0)
    
    if is_above:
        condition_met = current_price >= target_price
        direction = "über"
    else:
        condition_met = current_price <= target_price
        direction = "unter"
        
    if condition_met:
        print(f"ALARM: {ticker_symbol} ist jetzt bei {current_price:.2f}, "
              f"das ist {direction} deiner Schwelle von {target_price:.2f}!")
    
    # Wenn Datenbankverbindung übergeben wurde, Alarm speichern
    if conn:
        save_alert(conn, ticker_symbol, target_price, is_above)
    
    return condition_met

def monitor_stocks(ticker_symbols, check_interval=300, max_checks=None, conn=None):
    # Überwacht die Aktienkurse in regelmäßigen Abständen
    checks = 0
    while max_checks is None or checks < max_checks:
        print(f"\n---Aktualisierung {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}---")

        stock_data = get_current_data(ticker_symbols)
        
        # Wenn Datenbankverbindung übergeben wurde, Daten speichern
        if conn:
            save_current_data(conn, stock_data)
        
        # Alarme überprüfen, wenn Datenbankverbindung vorhanden
        if conn:
            alerts = get_saved_alerts(conn)
            for alert_id, symbol, target_price, is_above in alerts:
                if symbol in stock_data:
                    current_price = stock_data[symbol]["price"]
                    if (is_above and current_price >= target_price) or (not is_above and current_price <= target_price):
                        print(f"ALARM: {symbol} hat die Preisschwelle von {target_price:.2f} erreicht!")
                        # Optional: Alarm als inaktiv markieren
                        # cursor = conn.cursor()
                        # cursor.execute("UPDATE alerts SET is_active = 0 WHERE id = ?", (alert_id,))
                        # conn.commit()
        
        for symbol, data in stock_data.items():
            print(f"{data['name']} ({symbol}): {data['price']:.2f} EUR/USD, "
                  f"(Änderung: {data['change']:.2f}%)")
            
        checks += 1
        if max_checks is None or checks < max_checks:
            print(f"Nächste Aktualisierung in {check_interval // 60} Minuten...")
            time.sleep(check_interval)

def plot_price_history_from_db(conn, symbol):
    """Preishistorie aus der Datenbank visualisieren"""
    history = get_price_history(conn, symbol)
    
    if not history:
        print(f"Keine historischen Daten für {symbol} in der Datenbank gefunden.")
        return
    
    dates = [row[0] for row in history]
    prices = [row[1] for row in history]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, prices, marker='o', label=f'{symbol} Schlusskurs')
    
    # Durchschnittspreis hinzufügen
    avg_price = sum(prices) / len(prices)
    plt.axhline(avg_price, color='r', linestyle='--', label=f'Durchschnittspreis: {avg_price:.2f}')
    
    plt.title(f'{symbol} Kursverlauf (aus Datenbank)')
    plt.xlabel('Datum')
    plt.ylabel('Preis (EUR/USD)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    # Datenbank initialisieren
    conn = initialize_database()
    
    print("===AKTIEN-DATEN-TRACKER MIT DATENSPEICHERUNG===")
    
    while True:
        print("\nWas möchten Sie tun?")
        print("1. Aktuelle Kursdaten abrufen und speichern")
        print("2. Historische Daten visualisieren und speichern")
        print("3. Kursbenachrichtigung setzen")
        print("4. Aktienkurse überwachen")
        print("5. Gespeicherte Daten anzeigen")
        print("6. Gespeicherte Alarme anzeigen")
        print("7. Beenden")
        
        choice = input("Bitte wählen Sie eine Option (1-7): ")  
        
        if choice == "1": 
            symbols = input("Geben Sie die Ticker-Symbole (kommagetrennt) ein: ").split(",")
            symbols = [s.strip() for s in symbols]
            stock_data = get_current_data(symbols)
            
            for symbol, data in stock_data.items():
                print(f"{data['name']} ({symbol}): {data['price']:.2f} EUR/USD, "
                      f"(Änderung: {data['change']:.2f}%)")
            
            # Daten in Datenbank speichern
            save_current_data(conn, stock_data)
            
            plot_current_prices(stock_data)
            
        elif choice == "2":
            symbol = input("Geben Sie das Ticker-Symbol ein: ").strip()
            period = input("Geben Sie den Zeitraum ein (z.B. 1mo, 3mo, 1y): ").strip()
            plot_historical_data(symbol, period, conn)  # Datenbank-Verbindung übergeben
            
        elif choice == "3":
            symbol = input("Geben Sie das Ticker-Symbol ein: ").strip()
            price = float(input("Geben Sie den Zielpreis ein: "))
            direction = input("Benachrichtigung wenn Kurs über (o) oder unter (u) der Schwelle: ")
            is_above = direction.lower().startswith("o")
            set_price_alert(symbol, price, is_above, conn)  # Datenbank-Verbindung übergeben
            
        elif choice == "4":
            symbols = input("Geben Sie die Ticker-Symbole (kommagetrennt) ein: ").split(",")
            symbols = [s.strip() for s in symbols]
            interval = int(input("Geben Sie das Überwachungsintervall in Minuten ein: ")) * 60
            checks = input("Geben Sie die maximale Anzahl der Überprüfungen ein (0 für unendlich): ")
            max_checks = int(checks) if checks and int(checks) > 0 else None
            monitor_stocks(symbols, interval, max_checks, conn)  # Datenbank-Verbindung übergeben
            
        elif choice == "5":
            print("\nGespeicherte Kursdaten:")
            symbol_filter = input("Ticker-Symbol eingeben (leer lassen für alle): ").strip()
            
            symbols = [symbol_filter] if symbol_filter else None
            latest_prices = get_latest_prices(conn, symbols)
            
            if latest_prices:
                print("\nSymbol\tLetztes Update\t\tPreis\tÄnderung")
                print("-" * 50)
                for symbol, timestamp, price, change in latest_prices:
                    print(f"{symbol}\t{timestamp}\t{price:.2f}\t{change:.2f}%")
                
                # Option, gespeicherte Daten zu visualisieren
                visualize = input("\nMöchten Sie die Preishistorie eines Symbols visualisieren? (j/n): ")
                if visualize.lower() == "j":
                    symbol = input("Geben Sie das Ticker-Symbol ein: ").strip()
                    plot_price_history_from_db(conn, symbol)
            else:
                print("Keine gespeicherten Daten gefunden.")
                
        elif choice == "6":
            print("\nGespeicherte Preisalarme:")
            alerts = get_saved_alerts(conn)
            
            if alerts:
                print("\nID\tSymbol\tZielpreis\tRichtung")
                print("-" * 40)
                for alert_id, symbol, target_price, is_above in alerts:
                    direction = "über" if is_above else "unter"
                    print(f"{alert_id}\t{symbol}\t{target_price:.2f}\t\t{direction}")
            else:
                print("Keine aktiven Preisalarme gefunden.")
                
        elif choice == "7":
            print("Programm wird beendet.")
            conn.close()
            break
            
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

if __name__ == "__main__":
    main()