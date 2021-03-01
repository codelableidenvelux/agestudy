import csv
import os
import smtplib, ssl

import urllib.request
import pandas as pd

from flask import redirect, render_template, request, session
from functools import wraps
from dateutil.parser import parse
import string
import random
from datetime import datetime, timedelta


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
    It returns 0 if the user does not want to participate for monetary compensation

    It also is used to check if the user lives in the Netherlands
    returns 1 if they do and 0 if they dont
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
    if gender == "male":
        return 1
    elif gender == "female":
        return 2
    elif gender == "other":
        return 3

def total_money(df):
    df["time_exec"] = pd.to_datetime(df["time_exec"])
    total_survey_money = 0
    total_rt_money = 0
    total_tasks_money = 0
    df = df[df["user_type"] == 1]

    by_id = df.groupby(by="user_id")
    for (key, values) in by_id:
        for value in values["task_id"]:
            if value == 4:
                total_survey_money = total_survey_money + 2
            elif value == 5:
                total_survey_money = total_survey_money + 2

        per_month = values.groupby(by="month")
        for (key, value) in per_month:
            if 8 in value["task_id"].values:
                total_rt_money = total_rt_money + 0.25
            if 1 in value["task_id"].values or 2 in value["task_id"].values or 3 in value["task_id"].values:
                total_tasks_money = total_tasks_money + 1.75

    total = total_rt_money + total_tasks_money + total_survey_money
    money = {"total": total, "tasks": total_tasks_money, "survey": total_survey_money, "rt": total_rt_money}
    return money

def projected_money(num_p):
    # total tasks
    tasks = num_p * 1.75 * 12
    # total rt
    rt = num_p * 0.25 * 12
    # surveys
    sf_36 = num_p * 2.00 * 3
    phone_survey =  num_p * 2.00
    # total survey
    survey = sf_36 + phone_survey
    total = survey + rt + tasks * 3
    return {"total": total, "tasks": tasks, "survey": survey, "rt": rt}

def get_num_active_participants(groupby_object):
    num_active_participants = 0

    for (key, value) in groupby_object:
        today = datetime.now()
        months_participating = today.month - value["time_sign_up"].iloc[0].month
        num_test_per_month = len(value["month"].unique())
        if months_participating == num_test_per_month:
            num_active_participants = num_active_participants + 1
    return num_active_participants


def task_frequency(df):
    sf_36_done = 0
    sf_36= 0
    sf_36_p = 0

    phone_survey_done = 0
    phone_survey = 0
    phone_survey_p = 0

    rt_done = 0
    rt = 0
    rt_p = 0

    corsi_done = 0
    corsi = 0
    corsi_p = 0

    n_back_done = 0
    n_back= 0
    n_back_p = 0

    t_switch_done = 0
    t_switch = 0
    t_switch_p = 0

    by_id = df.groupby(by=["user_id", "status"])
    for (key, values) in by_id:
        for value in values["task_id"]:
            if value == 4 and key[1] == 1:
                sf_36_done = sf_36_done + 1
            elif value == 4 and key[1] == 0:
                sf_36 = sf_36 + 1
            elif value == 5 and key[1] == 1:
                phone_survey_done = phone_survey_done + 1
            elif value == 5 and key[1] == 0:
                phone_survey = phone_survey + 1
            elif value == 8 and key[1] == 1:
                rt_done = rt_done + 1
            elif value == 8 and key[1] == 0:
                rt = rt + 1
            elif value == 1 and key[1] == 1:
                corsi_done = corsi_done + 1
            elif value == 1 and key[1] == 0:
                corsi = corsi + 1
            elif value == 2 and key[1] == 1:
                n_back_done = n_back_done + 1
            elif value == 2 and key[1] == 0:
                n_back = n_back + 1
            elif value == 3 and key[1] == 1:
                t_switch_done = t_switch_done + 1
            else:
                t_switch = t_switch + 1

    by_id = df.groupby(by=["task_id", "user_id"])
    for (key, values) in by_id:
        if key[0] == 4:
            sf_36_p = sf_36_p + 1
        elif key[0] == 5:
            phone_survey_p = phone_survey_p + 1
        elif key[0] == 8:
            rt_p = rt_p + 1
        elif key[0] == 1:
            corsi_p = corsi_p + 1
        elif key[0] == 2:
            n_back_p = n_back_p + 1
        else:
            t_switch_p = t_switch_p + 1

    tasks = [{"task": "sf_36","complete": sf_36_done,"incomplete": sf_36},
            {"task": "phone_survey","complete": phone_survey_done,"incomplete": phone_survey},
            {"task": "rt","complete": rt_done,"incomplete": rt},
            {"task": "corsi","complete": corsi_done,"incomplete": corsi},
            {"task": "n_back","complete": n_back_done,"incomplete": n_back},
            {"task": "t_switch","complete": t_switch_done,"incomplete": t_switch}]

    tasks_p = [{"task": "sf_36","complete": sf_36_p, "incomplete": 0},
            {"task": "phone_survey","complete": phone_survey_p, "incomplete": 0},
            {"task": "rt","complete": rt_p, "incomplete": 0},
            {"task": "corsi","complete": corsi_p, "incomplete": 0},
            {"task": "n_back","complete": n_back_p, "incomplete": 0},
            {"task": "t_switch","complete": t_switch_p, "incomplete": 0}]

    return (tasks,tasks_p)

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
