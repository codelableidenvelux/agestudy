from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from tempfile import mkdtemp
from db.python_2_db2 import Db
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import preprocess_birthdate, remove_whitespace, preprocess_checkbox, preprocess_gender, login_required, send_email
import re

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

# Home page Login required
@app.route('/')
@login_required
def index():
    return render_template("index.html")

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


@app.route("/login", methods=["GET", "POST"])
def login():
    ### DONT FORGET IF NO PARTICIPATION CODE NO LOGIN !!!
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
