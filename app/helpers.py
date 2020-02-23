import csv
import os
import smtplib, ssl

import urllib.request
import pandas as pd

from flask import redirect, render_template, request, session
from functools import wraps
from dateutil.parser import parse

def read_csv(filename):
    df = pd.read_csv(filename, sep=",", index_col=0, encoding = "utf-8")
    df = df.to_dict()
    return df

def preprocess_birthdate(date):
    """
    Function preprocesses the input birthday from the register page,
    it uses dateutil library to parse the date and make sure its in the right
    format. It also strips the white spaces if there were any.
    Return format str yyyy-mm-01
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
        if session.get('user_id') is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def language_check(f):
    """
    Decorator function to set the chosen language

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def language_function(*args, **kwargs):
        if request.method == "GET":
            language = request.args.get('language')
            if language:
                if language.lower() == "english":
                    session['language'] = "english"
                elif language.lower() == "dutch":
                    session['language'] = "dutch"
        return f(*args, **kwargs)
    return language_function
