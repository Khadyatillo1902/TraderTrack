import csv
import datetime
import pytz
import requests
import urllib.parse
import uuid

from flask import redirect, render_template, request, session
from functools import wraps
import yfinance as yf


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"), (" ", "-"), ("_", "__"),
            ("?", "~q"), ("%", "~p"), ("#", "~h"),
            ("/", "~s"), ('"', "''")
        ]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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

"""def lookup(symbol):
    # Look up quote for symbol.
    symbol = symbol.upper()
    
    # Prepare API request with proper time range
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API URL
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={
                "User-Agent": "Mozilla/5.0",  # Fixed User-Agent
                "Accept": "text/csv"  # More specific accept header
            },
            timeout=10  # Added timeout
        )
        response.raise_for_status()

        # Parse CSV response
        quotes = list(csv.DictReader(response.text.splitlines()))
        if not quotes:
            return None

        # Get latest price
        latest_quote = quotes[-1]
        price = round(float(latest_quote["Adj Close"]), 2)
        
        return {
            "name": symbol,  # Added name for display purposes
            "price": price,
            "symbol": symbol
        }

    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Error fetching stock data: {e}")
        return None"""

def usd(value):
    """Format value as USD."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"