import random 

MAX_LINES = 3
MAX_BET = 10000
MIN_BET = 1

ROWS = 3
COLS = 3

symbol_count = {
    "🍒": 8,    # Cherry - most common, lowest payout
    "🍋": 6,    # Lemon - common
    "🍊": 4,    # Orange - less common  
    "⭐": 2,    # Star - rare, highest payout
}

symbol_value = {
    "🍒": 2,    # 2x multiplier
    "🍋": 3,    # 3x multiplier
    "🍊": 5,    # 5x multiplier
    "⭐": 10,   # 10x multiplier
}

def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        all_same = True
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                all_same = False
                break 
        
        if all_same:
            winnings += values[symbol] * bet 
            winning_lines.append(line + 1)
    
    return winnings, winning_lines 

def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, count in symbols.items(): 
        for _ in range(count):
            all_symbols.append(symbol)
    
    columns = []
    for col in range(cols):
        column = []
        for row in range(rows):
            value = random.choice(all_symbols)
            column.append(value)
        columns.append(column)
    
    return columns 

def print_slot_machine(columns):
    print("\n" + "="*15)
    for row in range(len(columns[0])):
        print("| ", end="")
        for i, column in enumerate(columns):
            if i != len(columns) - 1:  
                print(column[row], end=" | ")
            else:
                print(column[row], end="")
        print(" |")
    print("="*15)

def calculate_theoretical_rtp():
    """Calculate the theoretical Return to Player percentage"""
    total_symbols = sum(symbol_count.values())
    total_combinations = total_symbols ** 3
    
    expected_payout = 0
    for symbol, count in symbol_count.items():
        probability = (count / total_symbols) ** 3
        payout = symbol_value[symbol]
        expected_payout += probability * payout
    
    rtp = (expected_payout / 1) * 100  # RTP as percentage
    return rtp

def deposit(): 
    while True:
        amount = input("Type an amount you like to deposit $")
        if amount.isdigit():
            amount = int(amount) 
            if amount > 0:
                break 
            else:
                print("Amount must be positive")
        else: 
            print("Invalid Input. Amount must be a number")
    return amount 

def get_number_of_lines():
    while True:
        lines = input(f"Enter the number of lines to bet on (1-{MAX_LINES})? ")
        if lines.isdigit():
            lines = int(lines) 
            if 1 <= lines <= MAX_LINES:
                break 
            else:
                print("Enter a valid number")
        else: 
            print("Invalid Input. Must be a number")
    return lines
    
def get_bet():
    while True:
        amount = input(f"Type an amount you like to bet per line ${MIN_BET}-${MAX_BET}: $")
        if amount.isdigit():
            amount = int(amount)
            if MIN_BET <= amount <= MAX_BET:
                break 
            else:
                print(f"Amount must be between ${MIN_BET} and ${MAX_BET}")
        else: 
            print("Invalid Input. Amount must be a number")
    return amount 

def spin(balance):
    lines = get_number_of_lines()
    while True: 
        bet_size = get_bet()
        total_bet = lines * bet_size
        if total_bet > balance:
            print(f"Insufficient funds! Your current balance is ${balance}")
            print(f"Your total bet would be ${total_bet}")
        else:
            break 
     
    print(f"\nYou are betting ${bet_size} on {lines} lines. Total bet: ${total_bet}")
    
    slot = get_slot_machine_spin(ROWS, COLS, symbol_count)
    print_slot_machine(slot)
    
    winnings, winning_lines = check_winnings(slot, lines, bet_size, symbol_value)
    
    if winnings > 0:
        print(f"🎉 Congratulations! You won ${winnings}!")
        print(f"You won on line(s): {', '.join(map(str, winning_lines))}")
        net_result = winnings - total_bet
        if net_result > 0:
            print(f"Net profit: ${net_result}")
        else:
            print(f"Net loss: ${abs(net_result)}")
    else:
        print(" No wins this time. Better luck next spin!")
        print(f"You lost ${total_bet}")
    
    return winnings - total_bet

def show_paytable():
    print("\n" + "="*30)
    print("           PAYTABLE")
    print("="*30)
    print("Symbol | Payout (per $1 bet)")
    print("-" * 30)
    for symbol, payout in symbol_value.items():
        print(f"  {symbol}    |     ${payout}")
    print("="*30)
    print("Match 3 symbols on a line to win!")
    rtp = calculate_theoretical_rtp()
    print(f"Theoretical RTP: {rtp:.1f}%")
    print("="*30)

def main():
    print("🎰 Welcome to the Fair Slot Machine! 🎰")
    show_paytable()
    
    balance = deposit()
    
    while True:
        print(f"Current balance: ${balance}")
        action = input("Enter 'spin' to play, 'paytable' to see payouts, or 'quit' to exit: ").lower()
        
        if action in ['q', 'quit', 'exit']:
            break
        elif action in ['p', 'paytable', 'pay']:
            show_paytable()
        elif action in ['s', 'spin', '']:
            spin(balance)
            if balance <= 0:
                print("😞 You're out of money! Game over.")
                break

if __name__ == "__main__": 
    main()