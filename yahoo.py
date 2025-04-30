import yfinance as yf

def lookup(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        
        if data.empty:
            return None
            
        # Get the closing price and properly convert it
        close_price = data["Close"].iloc[-1]
        
        return {
            'name': stock.info.get("shortName", symbol),
            'price': round(float(close_price), 2),  # Correct float conversion
            'symbol': symbol
        }
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

# Test the function
result = lookup("AAPL")
print(result)