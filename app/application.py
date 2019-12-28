from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from tempfile import mkdtemp
from db.python_2_db2 import Db
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import preprocess_birthdate, remove_whitespace, preprocess_checkbox, preprocess_gender, login_required, send_email
import re
from datetime import datetime, timedelta

app = Flask(__name__)
key  = open("secret_key.txt", "r")
secret_key = key.read()
app.secret_key = secret_key


# Ensure templates are auto-reloaded
#app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# make an instance of the database class
db = Db("db/key.txt")

################################################################################
########################### TASK MANAGEMENT ####################################
###############################################################################
def task_opening(task_id):
    """
    This function keeps track of which task the user is doing
    Get the link to the task in psytoolkit
    Insert an open task in tracked_task
    a status of 0 means its open and a status of 1 means its completed
    """
    id = session["user_id"]

    select_link = f"SELECT TASK_LINK FROM TASKS WHERE TASK_ID={task_id}"
    link =  db.execute(select_link, 1)
    insert = f"INSERT INTO TRACKED_TASK (user_id, task_id, status) VALUES ({id},{task_id}, 0)"
    db.execute(insert, 0)

    # Testing
    #select = f"SELECT * FROM TRACKED_TASK WHERE USER_ID = {id}"
    #row = db.execute(select, 1)
    #print(row)
    return link

def task_completed(task_id):
    """
    This function keeps tracks of the completed tasks,
    select the last task the user followed
    If the task the user last started is the same as the task the user completed
    Update the status of the task to completed
    Insert the completed task in the table task_completed
    TODO: DO THIS AS TRANSACTION
    """
    id = session["user_id"]
    select = f"SELECT * FROM TRACKED_TASK WHERE time_exec= (SELECT MAX(time_exec) FROM TRACKED_TASK WHERE USER_ID = {id});"
    newest_task = db.execute(select, 1)
    print(newest_task)
    opened_task = newest_task[0]["TASK_ID"]
    if opened_task == task_id:
        update = f"UPDATE TRACKED_TASK SET status = 1 WHERE time_exec= (SELECT MAX(time_exec) FROM TRACKED_TASK WHERE USER_ID = {id});"
        insert = f"INSERT INTO TASK_COMPLETED (user_id, task_id) VALUES ({id}, {task_id});"
        db.execute(update, 0)
        db.execute(insert, 0)

################################################################################
##################### LINK TO CORSI TASK_ID = 0 ################################
###############################################################################
@app.route('/corsi', methods=["GET"])
@login_required
def corsi():
    task_id = 0
    link = task_opening(task_id)
    return redirect(link[0]["TASK_LINK"])

@app.route('/corsi_end', methods=["GET"])
@login_required
def corsi_end():
    task_id = 0
    task_completed(task_id)
    return render_template("end.html")

################################################################################
#################### LINK TO N_BACK TASK_ID = 1 ################################
###############################################################################
@app.route('/n_back', methods=["GET"])
@login_required
def n_back():
    task_id = 1
    link = task_opening(task_id)
    return redirect(link[0]["TASK_LINK"])

@app.route('/n_back_end', methods=["GET"])
@login_required
def n_back_end():
    task_id = 1
    task_completed(task_id)
    return render_template("end.html")

################################################################################
############# LINK TO TASK_SWITCHING TASK_ID = 2 ##############################
###############################################################################
@app.route('/task_switching', methods=["GET"])
@login_required
def task_switching():
    task_id = 2
    link = task_opening(task_id)
    return redirect(link[0]["TASK_LINK"])

@app.route('/task_switching_end', methods=["GET"])
@login_required
def task_switching_end():
    task_id = 2
    task_completed(task_id)
    return render_template("end.html")

################################################################################
##################### LINK TO SF-36 TASK_ID = 3 ################################
###############################################################################
@app.route('/sf_36', methods=["GET"])
@login_required
def sf_36():
    task_id = 3
    link = task_opening(task_id)
    return redirect(link[0]["TASK_LINK"])

@app.route('/sf_36_end', methods=["GET"])
@login_required
def sf_3_end():
    task_id = 3
    task_completed(task_id)
    return render_template("end.html")

################################################################################
################## LINK TO PHONE SURVEY TASK_ID = 4 ############################
###############################################################################
@app.route('/phone_survey', methods=["GET"])
@login_required
def phone_survey():
    task_id = 4
    link = task_opening(task_id)
    return redirect(link[0]["TASK_LINK"])

@app.route('/phone_survey_end', methods=["GET"])
@login_required
def phone_survey_end():
    task_id = 4
    task_completed(task_id)
    return render_template("end.html")


def should_show_task(task_id):
    """
    Looks for the last time the task was completed, then it calculates
    the next time the task will be available.
    if todays date is larger than the date where the task becomes available then
    return True, which indicated the button should be shown, the user can do the task
    else return False
    """
    id = session['user_id']
    select = f"SELECT MAX(time_exec) FROM TASK_COMPLETED WHERE USER_ID = {id} AND TASK_ID = {task_id}"
    last_timestamp = db.execute(select, 1)
    print(last_timestamp)
    if last_timestamp[0]["1"]:
        task_last_timestamp = last_timestamp[0]["1"]
        task = db.execute(f"SELECT FREQUENCY FROM TASKS WHERE TASK_ID={task_id}", 1)
        task_freq = round(float(task[0]["FREQUENCY"])*10*30,1)
        # TODO: REMOVE THIS LINE
        #task_freq = 1
        new_date = task_last_timestamp + timedelta(days=task_freq)
        if datetime.now() > new_date:
            return True
        else:
            return False
    else:
        return True

def calculate_money():
    """
    Calculate the amount of money the user has
    """
    id = session['user_id']
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = {id}"
    completed_tasks = db.execute(select, 1)
    money_earned = 0
    for i in completed_tasks:
        task_id = i["TASK_ID"]
        money = db.execute(f"SELECT PRICE FROM TASKS WHERE TASK_ID={task_id}" , 1)
        money_earned = money_earned + float(money[0]["PRICE"])
    return money_earned


################################################################################
################################ HOME PAGE #####################################
###############################################################################
# Home page Login required
@app.route('/', methods=["GET"])
@login_required
def index():
    if request.method == "GET":
        show_corsi  = should_show_task(0)
        show_n_back = should_show_task(1)
        show_task_switching = should_show_task(2)
        show_sf_36 = should_show_task(3)
        show_phone_survey = should_show_task(4)
        calculate_money()
        return render_template("index.html", show_corsi=show_corsi, show_n_back=show_n_back, show_task_switching=show_task_switching, show_sf_36=show_sf_36, show_phone_survey=show_phone_survey)

################################################################################
################################ REGISTER #####################################
###############################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # set to lowercase
        username_r = request.form.get("username").lower()
        # set to lowercase
        email_r = request.form.get("email").lower()
        for_money_r = request.form.get("money")
        collect_possible_r = request.form.get("collect_possible")
        birthdate_r = request.form.get("date")
        gender_r = request.form.get("gender")
        password = request.form.get("password")
        new_password = request.form.get("confirmation")

        # ensure that all fiels that are required were filled in correctly
        if not username_r or not birthdate_r or not gender_r or not email_r:
            flash("Fill in all fields")
            return render_template("register.html")

        # preprocesses inputs to get in right format for database
        username = remove_whitespace(username_r)
        email = remove_whitespace(email_r)
        for_money = preprocess_checkbox(for_money_r)
        collect_possible = preprocess_checkbox(collect_possible_r)
        user_type = 2
        if for_money and collect_possible:
            user_type = 1
        birthdate = preprocess_birthdate(birthdate_r)
        gender = preprocess_gender(gender_r)

        # Check if password matches and has a number, capital letter, lower case letter and minimum 5 characters
        if check_password(password, new_password):
            # encrypt the users' password
            hash = generate_password_hash(password)

            # check if the username is already in use
            select = "SELECT user_name FROM SESSION_INFO WHERE user_name = ?"
            rows = db.prepare(select, (username,), 1)
            # check true it means it is in use
            if rows:
                flash("Username already in use")
                return render_template("register.html")

            # add user to the database
            param = (username, email, gender, collect_possible, for_money, user_type, birthdate, hash)
            insert = "INSERT INTO session_info (user_name, email, gender, collect_possible, for_money, user_type, birthyear, pas_hash) VALUES (?,?,?,?,?,?,?,?)"
            result = db.prepare(insert, param, 0)

            select = "SELECT * FROM SESSION_INFO WHERE user_name = ?"
            rows = db.prepare(select, (username,), 1)
            # Remember which user has logged in
            session['user_id'] = rows[0]['USER_ID']
            # Redirect user to home page

            # send_email
            email_r  = open("email.txt", "r")
            email = email_r.read()
            pasw_r  = open("pass.txt", "r")
            pasw = pasw_r.read()
            message = 'Subject: Info \n\n username: ' + username + "\n email: " + email + "\n user_id: " + str(rows[0]['USER_ID']) + "\n user_type: " + str(user_type)
            send_email(email, pasw, message)

            return redirect("/")
        else:
            # the passwords did not match
            flash("Passwords did not match")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

# TODO: REMOVE
# If the user has registered succesfully they receive a confirmation page
# This tells them they will receive an email with the id
@app.route("/registered", methods=["GET", "POST"])
def registered():
    return render_template("registered.html")


@app.route("/availability", methods=["GET"])
def availability():
    """
    Checks the availability of the username
    Returns JSON with True or False
    """
    # set to lowercase
    username = request.args.get('username').lower()
    # get the user information
    select = "SELECT user_name FROM SESSION_INFO WHERE user_name = ?"
    rows = db.prepare(select, (username,), 1)
    return jsonify(len(rows) == 0)

################################################################################
################################ LOGIN  #######################################
###############################################################################

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # set to lowercase
        username = request.form.get("username").lower()
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            flash("must provide username")
            return render_template("login.html")
        # Ensure password was submitted
        elif not password:
            flash("must provide password")
            return render_template("login.html")

        # get the user information
        select = "SELECT * FROM SESSION_INFO WHERE user_name = ?"
        rows = db.prepare(select, (username,), 1)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['PAS_HASH'], request.form.get("password")):
            return "invalid username and/or password"

        # Remember which user has logged in
        session['user_id'] = rows[0]['USER_ID']
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

def check_password(password, new_password):
    """Make sure password is correctly chosen"""

    # ensure that all fiels were filled in correctly
    if password != new_password:
        return False

    # check if password has number, length and symbols
    number = len(re.findall(r"[0-9]", password))
    capital = len(re.findall(r"[A-Z]", password))
    lower = len(re.findall(r"[a-z]", password))
    return len(password) > 5 and number > 0 and capital > 0 and lower > 0

################################################################################
################################ LOGOUT #####################################
###############################################################################
@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

################################################################################
################################ ACCOUNT #####################################
###############################################################################
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    User can view their account information
    User can update their password
    """
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = ?"
        id=session["user_id"]
        rows = db.prepare(select, (id,), 1)

        if not check_password_hash(rows[0]['PAS_HASH'], old_password):
            flash("Password incorrect")
            return render_template("account.html")
        # check if the new password is properly implemented
        print(password, confirmation)
        if check_password(password, confirmation):
            # encrypt the users' password
            hash = generate_password_hash(password)
            update = "UPDATE SESSION_INFO SET pas_hash = ? WHERE USER_ID = ?"
            param = (hash,id)
            db.prepare(update, param, 0)
            flash("Password changed!")
            # Redirect user to home page
            return redirect("/")
        else:
            flash("One or more fields filled incorrectly")
            return render_template("account.html")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        id = session["user_id"]
        select_username = "SELECT USER_NAME FROM SESSION_INFO WHERE USER_ID = ?"
        username_row = db.prepare(select_username, (id,), 1)
        username = username_row[0]["USER_NAME"]
        return render_template("account.html", username=username.capitalize())

################################################################################
################################ STATIC #####################################
###############################################################################
@app.route("/consent", methods=["GET", "POST"])
@login_required
def consent():
    """
    Consent form
    """
    return render_template("consent.html")

@app.route("/eeg", methods=["GET", "POST"])
@login_required
def eeg():
    """
    EEG information
    """
    return render_template("eeg.html")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """
    Home page
    """
    return render_template("home.html")
