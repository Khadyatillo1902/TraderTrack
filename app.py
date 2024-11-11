import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["POST", "GET"])
@login_required
def index():
        try:
            user_id = session["user_id"]

            rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
            cash = rows[0]["cash"]

            holdings = db.execute("SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)

            stocks = []
            total_value = 0

            for holding in holdings:

                symbol = holding["symbol"]
                total_shares = holding["total_shares"]

                quote = lookup(symbol)

                if quote is None:
                    return apology("invalid symbol", 400)

                current_price = quote["price"]
                total_stock_value = total_shares * current_price

                stocks.append({
                    "symbol": symbol,
                    "shares": total_shares,
                    "price": current_price,
                    "total": total_stock_value,
                })

                total_value += total_stock_value

            grand_total = total_value + cash

            return render_template("index.html", stocks=stocks, cash=cash, grand_total=grand_total)
        
        except Exception as e:
            print(f"Error: {e}")
            return apology("Error occured", 500)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        # Retrieve form inputs
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate inputs
        if not symbol:
            return apology("must provide symbol", 400)

        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("share must be positive", 400)

        shares = int(shares)

        # Lookup the stock symbol
        quote = lookup(symbol)

        # Ensure the symbol is valid
        if quote is None:
            return apology("invalid symbol", 400)

        user_id = session["user_id"]

        # Retrieve user's current cash
        rows = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

        if len(rows) != 1:
            return apology("couldn't fetch user's cash", 400)

        cash = rows[0]["cash"]

        total_cost = shares * quote["price"]

        # Check if the user can afford the shares
        if cash < total_cost:
            return apology("can't afford", 400)

        # Record the purchase in the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, ?)",
                   user_id, quote["symbol"], shares, quote["price"], "buy")

        # Update user's cash balance
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, user_id)

        flash(f"You bought {shares} shares of {symbol}!", 'success')

        # Redirect to home page
        return redirect("/")
    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():

    user_id = session["user_id"]

    transactions = db.execute("SELECT symbol, shares, price, transaction_type, transaction_time FROM transactions WHERE user_id = ? ORDER BY transaction_time DESC", user_id)

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("must provide a symbol", 400)

        quote = lookup(symbol)

        if quote is None:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

       username = request.form.get("username")
       password = request.form.get("password")
       confirmation = request.form.get("confirmation")

       if not username:
           return apology("must provide username", 400)

       if not password:
           return apology("must provide password", 400)

       if not confirmation:
           return apology("must retype password", 400)

       if password != confirmation:
           return apology("passwords don't match", 400)

       hash = generate_password_hash(password)

       try:
           db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
       except ValueError:
           return apology("username already exists", 400)

       return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("provide stock symbol", 400)

        if not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("must provide a positive number of shares", 400)

        shares = int(shares)

        quote = lookup(symbol)

        if quote is None:
            return apology("invalid symbol", 400)

        user_id = session["user_id"]
        user_shares = db.execute("SELECT SUM(shares) AS total_shares FROM transactions WHERE user_id = ? AND symbol = ?", user_id, symbol)

        if not user_shares or user_shares[0]["total_shares"] is None or user_shares[0]["total_shares"] < shares:
            return apology("not enough shares", 400)

        total_value = shares * quote["price"]

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, 'sell')",
                   user_id, symbol, -shares, quote["price"])
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_value, user_id)

        flash(f"You sold {shares} shares of {symbol}!", 'success')

        return redirect("/")

    else:
        user_id = session["user_id"]
        stocks = db.execute("SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)

        return render_template("sell.html", quote=stocks)


