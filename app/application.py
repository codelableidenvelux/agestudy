from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from tempfile import mkdtemp
from db.python_2_db2 import Db
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import preprocess_birthdate, remove_whitespace, preprocess_checkbox, preprocess_gender, login_required, send_email, read_csv
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
layout = read_csv("static/csv/layout.csv")
print(layout["list1"])
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
        insert = f"INSERT INTO TASK_COMPLETED (user_id, task_id, collect) VALUES ({id}, {task_id}, 1);"
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
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = {id} AND COLLECT NOT IN ( 0 )"
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
    register = read_csv("static/csv/register.csv")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # set to lowercase
        username_r = request.form.get("username").lower()
        # set to lowercase
        email_r = request.form.get("email").lower()
        for_money_r = request.form.get("money")
        collect_possible_r = request.form.get("collect_possible")
        year = request.form.get("year")
        month = request.form.get("month")
        birthdate_r = str(year) + str(month) + "01"
        gender_r = request.form.get("gender")
        password = request.form.get("password")
        new_password = request.form.get("confirmation")

        # ensure that all fiels that are required were filled in correctly
        if not username_r or not birthdate_r or not gender_r or not email_r:
            flash("Fill in all fields")
            return render_template("register.html",  register=register)

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
                return render_template("register.html",  register=register)

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
        return render_template("register.html",  register=register)


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

@app.route("/email", methods=["GET"])
def email():
    """
    Checks the availability of the username
    Returns JSON with True or False
    """
    # set to lowercase
    username = request.args.get('username').lower()
    email = request.args.get('email').lower()
    # get the user information
    return jsonify(username == email)

################################################################################
################################ LOGIN  #######################################
###############################################################################

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    login_csv = read_csv("static/csv/login.csv")
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
            flash("invalid username and/or password")
            return render_template("login.html", login_csv=login_csv)

        # Remember which user has logged in
        session['user_id'] = rows[0]['USER_ID']
        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", login_csv=login_csv)

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
    account_csv = read_csv("static/csv/account.csv")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # change password, get old password and two new entries
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # select users information
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = ?"
        id=session["user_id"]
        rows = db.prepare(select, (id,), 1)
        username = rows[0]["USER_NAME"]
        email = rows[0]["EMAIL"]


        # Check if the old password matches
        if not check_password_hash(rows[0]['PAS_HASH'], old_password):
            flash("Password incorrect")
            return render_template("account.html", account_csv=account_csv, username=username.capitalize(), email=email)
        # check if the new password is properly implemented
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
            return render_template("account.html", account_csv=account_csv, username=username.capitalize(), email=email)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show them their account information
        id = session["user_id"]
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = ?"
        rows = db.prepare(select, (id,), 1)
        username = rows[0]["USER_NAME"]
        email = rows[0]["EMAIL"]
        return render_template("account.html", account_csv=account_csv, username=username.capitalize(), email=email)

################################################################################
################################ STATIC #####################################
###############################################################################
@app.route("/consent", methods=["GET", "POST"])
@login_required
def consent():
    """
    Consent form
    """
    consent_csv = read_csv("static/csv/consent.csv")
    return render_template("consent.html", consent_csv=consent_csv)

@app.route("/eeg", methods=["GET", "POST"])
@login_required
def eeg():
    """
    EEG information
    """
    eeg_csv = read_csv("static/csv/eeg.csv")
    sent_email_csv = read_csv("static/csv/sent_email.csv")
    # If they clicked on the submit button
    if request.method == "POST":
        id = session["user_id"]
        # select the user info
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = ?"
        rows = db.prepare(select, (id,), 1)

        # send_email with the users info to our server to contact them about participating
        email_r  = open("email.txt", "r")
        email = email_r.read()
        pasw_r  = open("pass.txt", "r")
        pasw = pasw_r.read()
        message = 'Subject: EEG \n\n The following participant wants to participate in the EEG study' + '\n username: ' + str(rows[0]['USER_NAME']) + "\n email: " + str(rows[0]['EMAIL']) + "\n user_id: " + str(rows[0]['USER_ID']) + "\n user_type: " + str(str(rows[0]['USER_TYPE']))
        send_email(email, pasw, message)

        # render a thank you page
        return render_template("sent_email.html", sent_email_csv=sent_email_csv)
    else:
        return render_template("eeg.html", eeg_csv=eeg_csv)

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    """
    Home page, contains a money tab and a recommended task
    """
    home_csv = read_csv("static/csv/home.csv")
    # calculate the money earned to draw the barchart
    price = calculate_money()

    # make the recomendation system which will recommend one task, show only 1 div
    id = session["user_id"]
    # select all the completed tasks
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = {id}"
    rows = db.execute(select, 1)

    # select the user type to see if money barchart should be shown
    select = f"SELECT USER_TYPE FROM SESSION_INFO WHERE USER_ID = {id}"
    user_type_row = db.execute(select, 1)
    # user type of 1 indicates they want and are able to participate for money
    if user_type_row[0]["USER_TYPE"] == 1:
        user_type = True
    # user type of 2 indicates they are unable to participate for money
    else:
        user_type = False
    recomendation = True
    # put the completed tasks in a list
    completed_tasks = []
    for i in rows:
        completed_tasks.append(i["TASK_ID"])

    # First recomendation is to do the phone survey
    if 4 not in completed_tasks or should_show_task(4):
        task = {"img":"/static/images/phone_survey.png", "alt":"Phone survey", "title":"Phone survey",  "text" : "Placeholder Phone survey task", "link" : "/phone_survey", "button_text": "Try Phone survey"}
    # Second recomendation is to do the sf-36
    elif 3 not in completed_tasks or should_show_task(3):
        task = {"img":"/static/images/SF_36.png", "alt":"sf_36", "title":"SF-36",  "text" : "Placeholder SF-36 task", "link" : "/sf_36", "button_text": "Try SF-36"}
    # Third recomendation is to do corsi task
    elif  0 not in completed_tasks or should_show_task(0):
        task = {"img":"/static/images/corsi.png", "alt":"corsi",  "title" : "Corsi", "text" : "Placeholder corsi task", "link" : "/corsi", "button_text": "Try corsi"}
    # Fourth recomendation is to do n_back task
    elif 1 not in completed_tasks or should_show_task(1):
        task = {"img":"/static/images/N_back.png", "alt":"N-back", "title" : "N-back", "text" : "Placeholder n_back task", "link" : "/n_back", "button_text": "Try N-back"}
    # Fifth recomendation is to do task switching task
    elif 2 not in completed_tasks or should_show_task(2):
        task = {"img":"/static/images/task_switching.png", "alt":"task switching", "title" : "Task switching", "text" : "Placeholder task_switching task", "link" : "/task_switching", "button_text": "Try Task switching"}
    # If all tasks have been completed and are locked then give no recommendation dont show the div
    else:
        recomendation = False
        task = {"img":"", "alt":"", "title":"",  "text" : "", "link" : "", "button_text": ""}
    return render_template("home.html", price=price, user_type=user_type, recomendation=recomendation, home_csv=home_csv, img=task["img"], alt=task["alt"], title=task["title"], text=task["text"], link=task["link"], button_text=task["button_text"])

@app.route("/collection", methods=["POST"])
@login_required
def collection():
    """
    Button to collect payment
    """
    collected_csv = read_csv("static/csv/collected.csv")
    collection = request.form.get("collection")
    id = session["user_id"]
    # update the collection to 0 which means that the user has/will collect the money_earned
    # otherwise collect is 1
    update = f"UPDATE TASK_COMPLETED SET COLLECT=0 WHERE USER_ID = {id}"
    db.prepare(update, (id,), 0)

    # select the user info
    select = f"SELECT * FROM SESSION_INFO WHERE USER_ID = {id}"
    rows = db.prepare(select, (id,), 1)
    money_earned = calculate_money()

    # send_email with the users info to our email to contact them about participating
    # email contains username, email, usertype, user_id and the ammount to be collect
    email_r  = open("email.txt", "r")
    email = email_r.read()
    pasw_r  = open("pass.txt", "r")
    pasw = pasw_r.read()
    message = 'Subject: Payment collection \n\n The following participant wants to collect their payment for the study' + '\n username: ' + str(rows[0]['USER_NAME']) + "\n email: " + str(rows[0]['EMAIL']) + "\n user_id: " + str(rows[0]['USER_ID']) + "\n user_type: " + str(rows[0]['USER_TYPE']) + "\n ammount to collect: " + str(money_earned)
    send_email(email, pasw, message)

    # render a thank you page
    return render_template("collected.html", money_earned=money_earned, collected_csv=collected_csv)

@app.route("/about_study", methods=["GET"])
def about_study():
    about_study_csv = read_csv("static/csv/about_study.csv")
    return render_template("about_study.html", about_study_csv=about_study_csv)

@app.route("/for_participant", methods=["GET"])
def for_participant():
    for_participant_csv = read_csv("static/csv/for_participant.csv")
    return render_template("for_participant.html", for_participant_csv=for_participant_csv)

@app.route("/about_app", methods=["GET"])
def about_app():
    about_app_csv = read_csv("static/csv/about_app.csv")
    return render_template("about_app.html", about_app_csv=about_app_csv)

@app.route("/contact", methods=["GET"])
def contact():
    contact_csv = read_csv("static/csv/about_study.csv", contact_csv=contact_csv)
    return render_template("contact.html")
