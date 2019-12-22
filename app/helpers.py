import csv
import os
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
from dateutil.parser import parse


def preprocess_birthdate(date):
    """
    Function preprocesses the input birthday from the register page,
    it uses dateutil library to parse the date and make sure its in the right
    format. It also strips the white spaces if there were any.
    Return format str yyyy-mm-dd
    """
    dt = parse(date)
    return (dt.strftime('%Y-%m-%d'))

def preprocess_checkbox(input):
    """
    Function preprocesses the input user type from the register page,
    it return 1 if the box was checked meaning the user does want to participate
    for monetary compensation.
    It returns 2 if the user does not want to participate for monetary compensation

    It also is used to check if the user lives in the Netherlands
    returns 1 if they do and 2 if they dont
    """
    if input == "on":
        return 1
    else:
        return 0

def preprocess_gender(gender):
    """
    Function preprocesses the input gender from the register page,
    Returns 1 for male, 2 for female and 3 for other
    """
    if gender == "Male":
        return 1
    elif gender == "Female":
        return 2
    else:
        return 3

def remove_whitespace(input):
    return input.replace(' ', '')

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session.get('user_id'))
        if session.get('user_id') is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # Reject symbol if it contains comma
    if "," in symbol:
        return None

    # Query Alpha Vantage for quote
    # https://www.alphavantage.co/documentation/
    try:

        # GET CSV
        url = f"https://www.alphavantage.co/query?apikey={os.getenv('API_KEY')}&datatype=csv&function=TIME_SERIES_INTRADAY&interval=1min&symbol={symbol}"
        webpage = urllib.request.urlopen(url)

        # Parse CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())
        # Ignore first row
        next(datareader)

        # Parse second row
        row = next(datareader)

        # Ensure stock exists
        try:
            price = float(row[4])
        except:
            return None

        name = lookup_name(symbol)

        if not name:
            return None

        # Return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
        return {
            "price": price,
            "symbol": symbol.upper(),
            "name": name
        }

    except:
        return None


def lookup_name(symbol):
    """Look up name for symbol."""
    try:
        url = f"https://www.alphavantage.co/query?apikey={os.getenv('API_KEY')}&datatype=csv&function=SYMBOL_SEARCH&keywords={symbol}"
        webpage = urllib.request.urlopen(url)

        # Parse CSV
        datareader = csv.reader(webpage.read().decode("utf-8").splitlines())
        # Ignore first row
        next(datareader)

        # Parse second row
        row = next(datareader)

        return row[1]
    except:
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
