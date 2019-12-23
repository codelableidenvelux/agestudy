import csv
import os
import smtplib, ssl

import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
from dateutil.parser import parse


def preprocess_birthdate(date):
    """
    Function preprocesses the input birthday from the register page,
    it uses dateutil library to parse the date and make sure its in the right
    format. It also strips the white spaces if there were any.
    Return format str yyyy-mm-01
    """
    dt = parse(date)
    return (dt.strftime('%Y-%m-01'))

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

def send_email(sender_email, password, message):
    """
    This function takes an input email and password from sender and an input
    email from receiver. It sends an email with input text.
    """
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = 'ruchellakock@gmail.com' # Enter your address
    receiver_email = 'ruchellakock@gmail.com'  # Enter receiver address
    password = 'catcatcat'

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, sender_email, message)
