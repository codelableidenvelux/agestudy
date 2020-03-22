from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from tempfile import mkdtemp
from db.postgresql import Db
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
import re
from datetime import datetime, timedelta
import string
import requests

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
db = Db(app.logger)
layout = read_csv("static/csv/layout.csv")
login_csv = read_csv("static/csv/login.csv")
end_csv = read_csv("static/csv/end_task.csv")
payment_csv = read_csv("static/csv/payment.csv")
tasks = read_csv("static/csv/index.csv")
register_csv = pd.read_excel('static/csv/register.xlsx', index_col="tag")
account_csv = read_csv("static/csv/account.csv")
consent_csv = pd.read_excel('static/csv/consent.xlsx', index_col="tag")
email_unsent = read_csv("static/csv/email_unsent.csv")
eeg_csv = pd.read_excel('static/csv/eeg.xlsx', index_col="tag")
sent_email_csv = read_csv("static/csv/sent_email.csv")
home_csv = read_csv("static/csv/home.csv")
collected_csv = read_csv("static/csv/collected.csv")
about_study_csv = read_csv("static/csv/about_study.csv")
for_participant_csv = pd.read_excel('static/csv/for_participant.xlsx', index_col="tag")
about_app_csv = pd.read_excel('static/csv/about_app.xlsx', index_col="tag")
contact_csv = read_csv("static/csv/contact.csv")

# See which language was chosen and update the language
def language_set():
    language = request.args.get('language')
    if language:
        if language.lower() == "english":
            session['language'] = "english"
        elif language.lower() == "dutch":
            session['language'] = "dutch"
    # set the default language
    if "language" not in session:
        session["language"] = "english"

# Force user to a save location
@app.before_request
def before_request():
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme and scheme == 'http' and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

################################################################################
########################### TASK MANAGEMENT ####################################
###############################################################################
def int2base(x, base):
    digs = string.ascii_letters + string.digits
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[int(x % base)])
        x = int(x / base)

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)

def generate_id(id):
    """
    This function takes the user' id and transforms it into a
    8 digit id.
    """
    digs = string.ascii_letters + string.digits
    x = int2base(id, 62)
    for i in range(8):
        if len(x) < 8:
            x = digs[0] + x
    return x

def task_opening(task_id):
    """
    This function keeps track of which task the user is doing
    Get the link to the task in psytoolkit
    Insert an open task in tracked_task
    a status of 0 means its open and a status of 1 means its completed
    """
    id = session["user_id"]
    if session["language"] == "english":
        select_link = f"SELECT TASK_LINK FROM TASKS WHERE TASK_ID=(%s)"
    else:
        select_link = f"SELECT dutch_link FROM TASKS WHERE TASK_ID=(%s)"

    link =  db.execute(select_link, (task_id, ), 1)
    insert = f"INSERT INTO TRACKED_TASK (user_id, task_id, status) VALUES (%s, %s, %s)"
    insert_values = (id, task_id, 0)
    db.execute(insert, insert_values, 0)

    return link

def task_completed(task_id):
    """
    This function keeps tracks of the completed tasks,
    select the last task the user followed
    If the task the user last started is the same as the task the user completed
    Update the status of the task to completed
    Insert the completed task in the table task_completed
    """
    id = session["user_id"]
    select = f"SELECT * FROM TRACKED_TASK WHERE time_exec= (SELECT MAX(time_exec) FROM TRACKED_TASK WHERE USER_ID = (%s));"
    newest_task = db.execute(select, (id,), 1)
    opened_task = newest_task[0]["task_id"]
    if opened_task == task_id:
        update = f"UPDATE TRACKED_TASK SET status = 1 WHERE time_exec= (SELECT MAX(time_exec) FROM TRACKED_TASK WHERE USER_ID = (%s));"
        insert = f"INSERT INTO TASK_COMPLETED (user_id, task_id, collect) VALUES (%s, %s, 1);"
        db.execute(update, (id,), 0)
        db.execute(insert, (id, task_id), 0)

def send_email(message, username):
    """
    This function takes an input email and password from sender and an input
    email from receiver. It sends an email with input text.
    """
    try:
        email_r  = open("email.txt", "r")
        email = email_r.read().strip('\n')
        pasw_r  = open("pass.txt", "r")
        pasw = pasw_r.read().strip('\n')

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
            server.login(email, pasw)
            server.sendmail(email, "agestudy@fsw.leidenuniv.nl", message)
        return True
    except:
        app.logger.info('%s tried to send the following email: %s. There was an error', username, message)
        return False

################################################################################
##################### LINK TO CORSI TASK_ID = 0 ################################
###############################################################################
@app.route('/corsi', methods=["GET"])
@login_required
def corsi():
    """
    This function gives the link to the corsi task in psytoolkit
    """
    task_id = 1
    link = task_opening(task_id)
    return redirect(link[0][0]+ "&user_id=" + generate_id(session["user_id"]))

@app.route('/corsi_end', methods=["GET"])
@login_required
@language_check
def corsi_end():
    """
    This function redirects user to a thank you page. It registers that they have completed the task (thus updating their money earned)
    """
    task_id = 1
    task_completed(task_id)
    return render_template("end_task.html", end_csv=end_csv[session["language"]], layout=layout[session["language"]])

################################################################################
#################### LINK TO N_BACK TASK_ID = 1 ################################
###############################################################################
@app.route('/n_back', methods=["GET"])
@login_required
def n_back():
    task_id = 2
    link = task_opening(task_id)
    return redirect(link[0][0]+ "&user_id=" + generate_id(session["user_id"]))

@app.route('/n_back_end', methods=["GET"])
@login_required
@language_check
def n_back_end():
    task_id = 2
    task_completed(task_id)
    return render_template("end_task.html", end_csv=end_csv[session["language"]], layout=layout[session["language"]])

################################################################################
############# LINK TO TASK_SWITCHING TASK_ID = 2 ##############################
###############################################################################
@app.route('/task_switching', methods=["GET"])
@login_required
def task_switching():
    task_id = 3
    link = task_opening(task_id)
    return redirect(link[0][0]+ "&user_id=" + generate_id(session["user_id"]))

@app.route('/task_switching_end', methods=["GET"])
@login_required
@language_check
def task_switching_end():
    task_id = 3
    task_completed(task_id)
    return render_template("end_task.html", end_csv=end_csv[session["language"]], layout=layout[session["language"]])

################################################################################
##################### LINK TO SF-36 TASK_ID = 3 ################################
###############################################################################
@app.route('/sf_36', methods=["GET"])
@language_check
@login_required
def sf_36():
    task_id = 4
    link = task_opening(task_id)
    return redirect(link[0][0]+ "&user_id=" + generate_id(session["user_id"]))

@app.route('/sf_36_end', methods=["GET"])
@login_required
@language_check
def sf_3_end():
    task_id = 4
    task_completed(task_id)
    return render_template("end_task.html", end_csv=end_csv[session["language"]], layout=layout[session["language"]])

################################################################################
################## LINK TO PHONE SURVEY TASK_ID = 4 ############################
###############################################################################
@app.route('/phone_survey', methods=["GET"])
@login_required
def phone_survey():
    task_id = 5
    link = task_opening(task_id)
    return redirect(link[0][0]+ "&user_id=" + generate_id(session["user_id"]))

@app.route('/phone_survey_end', methods=["GET"])
@login_required
@language_check
def phone_survey_end():
    task_id = 5
    task_completed(task_id)
    return render_template("end_task.html", end_csv=end_csv[session["language"]], layout=layout[session["language"]])


def should_show_task(task_id):
    """
    Looks for the last time the task was completed, then it calculates
    the next time the task will be available.
    if todays date is larger than the date where the task becomes available then
    return True, which indicated the button should be shown, the user can do the task
    else return False
    """
    id = session['user_id']
    select = f"SELECT MAX(time_exec) FROM TASK_COMPLETED WHERE USER_ID = (%s) AND TASK_ID = (%s)"
    values = (id, task_id)
    last_timestamp = db.execute(select, values, 1)
    # [0][0] the second 0 refers to the maximum value
    if last_timestamp[0][0]:
        task_last_timestamp = last_timestamp[0][0]
        task = db.execute(f"SELECT FREQUENCY FROM TASKS WHERE TASK_ID=(%s)",(task_id,), 1)
        #task_freq = round(float(task[0]["frequency"])*10*30,1)
        task_freq = round(float(task[0]["frequency"])*10*30,1)
        new_date = task_last_timestamp + timedelta(days=task_freq)
        if datetime.now() > new_date:
            return True
        else:
            return False
    else:
        return True

def calculate_money():
    """
    Calculate the total amount of money the user has earned since last payment collection
    """
    id = session['user_id']
    # get the completed tasks where the user has not completed payment
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s) AND COLLECT NOT IN ( 0 )"
    completed_tasks = db.execute(select, (id,), 1)

    # Select all the tasks (even if the payment has been collected already)
    select_all_tasks = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s)"
    all_tasks = db.execute(select, (id,), 1)

    # Assume that payment for task can be connected (because they have not collected payment this month yet)
    can_collect_task_this_month = True
    # go over all the tasks
    for i in all_tasks:
        # check if a task (not a survey) has been performed this month AND check if payment has alread been collected this month
        # If this is true, since payment for tasks can only be collected once a month set can_collect_task_this_month to false
        if type(i[-1]) is datetime:
            if (i[2] != 4 or i[2] != 5) and i[-1].month == datetime.now().month:
                can_collect_task_this_month = False


    # seperate each task per month
    months_dict = {}
    for task in completed_tasks:
        if task[0].month in months_dict:
            months_dict[task[0].month].append(task)
        else:
            months_dict[task[0].month] = [task]
    # this is the total amount earned
    money_earned = 0
    # this is the amount only for the tasks
    money_earned_tasks = 0

    # Go over every month in the dictionary
    for month in months_dict:
        # Go over every value in that month
        for i in months_dict[month]:
            # select task_id
            task_id = i[2]
            # get the price for that task
            money = db.execute(f"SELECT PRICE FROM TASKS WHERE TASK_ID=(%s)", (task_id,), 1)

            # check if its a survey if it is then the user automatically gets paid the price of the survey
            if i[2] == 4 or i[2] == 5:
                money_earned = money_earned + float(money[0]["price"])
            # if it is a task then
            else:
                # calculate the ammount earned for tasks
                money_earned_tasks = money_earned_tasks + float(money[0]["price"])
                # Check if its smaller than the max value per month add it to the total amount earned
                if money_earned_tasks < (80-(10.5+1.75))/(12*3) and can_collect_task_this_month:
                    money_earned = money_earned + money_earned_tasks
        # set the amount for the tasks to 0 every month as not to go over the total value
        money_earned_tasks = 0
        # round to 2 decimals
    return round(money_earned, 2)


################################################################################
################################ HOME PAGE #####################################
###############################################################################
# Home page Login required
@app.route('/', methods=["GET"])
@login_required
@language_check
def index():
    if request.method == "GET":
        show_corsi  = should_show_task(1)
        show_n_back = should_show_task(2)
        show_task_switching = should_show_task(3)
        show_sf_36 = should_show_task(4)
        show_phone_survey = should_show_task(5)
        calculate_money()
        return render_template("index.html", layout=layout[session["language"]], tasks=tasks[session["language"]], show_corsi=show_corsi, show_n_back=show_n_back, show_task_switching=show_task_switching, show_sf_36=show_sf_36, show_phone_survey=show_phone_survey)

################################################################################
################################ REGISTER #####################################
###############################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    preferred_language = "english"
    if "language" in session:
        preferred_language = session["language"]
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        session["language"] = preferred_language
        # api-endpoint
        URL = "https://www.google.com/recaptcha/api/siteverify"

        # location given here
        location = "delhi technological university"

        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'secret':"6LfltOIUAAAAAERDowV2X1Tavbry5jjfq5IqDeCW", 'response': request.form.get("g-recaptcha-response")}

        # sending get request and saving the response as response object
        r = requests.get(url = URL, params = PARAMS)

        # extracting data in json format
        data = r.json()
        if not data["success"]:
            flash("Please click on the I am not a robot checkbox")
            return render_template("register.html",   consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])


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
            return render_template("register.html",   consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

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
            select = "SELECT user_name FROM SESSION_INFO WHERE user_name = (%s)"
            rows = db.execute(select, (username,), 1)
            # check true it means it is in use
            if rows:
                flash("Username already in use")
                return render_template("register.html",   consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

            # add user to the database
            param = (username, email, gender, collect_possible, for_money, user_type, birthdate, hash)
            insert = "INSERT INTO session_info (user_name, email, gender, collect_possible, for_money, user_type, birthyear, pas_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            result = db.execute(insert, param, 0)

            select = "SELECT * FROM SESSION_INFO WHERE user_name = %s"
            rows = db.execute(select, (username,), 1)
            # Remember which user has logged in
            session['user_id'] = rows[0][0]
            #session['language'] = rows[0]['USER_ID']
            # Redirect user to home page

            # send_email
            message = 'Subject: New Participant \n\n username: ' + username + "\n email: " + email + "\n user_id: " + str(rows[0][0]) + "\n user_type: " + str(user_type)
            send_email(message, username)

            return redirect("/home")
        else:
            # the passwords did not match
            flash("Passwords did not match")
            return render_template("register.html",   consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        session["language"] = preferred_language
        language_set()
        return render_template("register.html",  consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])


@app.route("/availability", methods=["GET"])
def availability():
    """
    Checks the availability of the username
    Returns JSON with True or False
    """
    # set to lowercase
    username = request.args.get('username').lower()
    # get the user information
    select = "SELECT user_name FROM SESSION_INFO WHERE user_name = (%s)"
    rows = db.execute(select, (username,), 1)
    return jsonify(len(rows) == 0)

@app.route("/session_pc", methods=["GET"])
def session_pc():
    """
    Checks if the checkbox on index.html has been checked already
    this is done by checking the session["pc"]
    """
    if request.args.get('checked') == "true":
        session["pc"] = True
    else:
        session["pc"] = False
    return jsonify(session["pc"])

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
    preferred_language = "english"
    if "language" in session:
        preferred_language = session["language"]
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        session["language"] = preferred_language
        # set to lowercase
        username = request.form.get("username").lower()
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            flash("Must provide email address")
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])
        # Ensure password was submitted
        elif not password:
            flash("Must provide password")
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])

        # get the user information
        select = "SELECT * FROM SESSION_INFO WHERE user_name = (%s)"
        rows = db.execute(select, (username,), 1)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['pas_hash'], request.form.get("password")):
            flash("Invalid username and/or password")
            if len(rows) != 1:
                app.logger.info('%s invalid username', username)
            else:
                app.logger.info('%s invalid password with email combination', username)
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])

        # Remember which user has logged in
        session['user_id'] = rows[0]['user_id']
        session['consent'] = rows[0]['consent']

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        session["language"] = preferred_language
        language_set()
        return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])

def check_password(password, new_password):
    """Make sure password is correctly chosen"""

    # ensure that all fiels were filled in correctly
    if password != new_password:
        return False

    # check if password has number, length and symbols
    number = len(re.findall(r"[0-9]", password))
    return len(password) > 5 and number > 0

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

@app.route("/pc", methods=["POST"])
@login_required
def pc():
    """
    This function stores if the user is on a pc in the session
    """
    if request.form.get("pc"):
        session["pc"] = 1
        print(session["pc"])
    print("hey")

################################################################################
################################ ACCOUNT #####################################
###############################################################################
@app.route("/account", methods=["GET", "POST"])
@login_required
@language_check
def account():
    """
    User can view their account information
    User can update their password
    """
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # change password, get old password and two new entries
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # select users information
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = (%s)"
        id=session["user_id"]
        rows = db.execute(select, (id,), 1)
        username = rows[0]["user_name"]
        email = rows[0]["email"]


        # Check if the old password matches
        if not check_password_hash(rows[0]['pas_hash'], old_password):
            flash("Password incorrect")
            app.logger.warning('%s Tried to change password in the /account but old password was incorrect', username)
            return render_template("account.html", account_csv=account_csv[session["language"]], username=username.capitalize(), email=email, layout=layout[session["language"]])
        # check if the new password is properly implemented
        if check_password(password, confirmation):
            # encrypt the users' password
            hash = generate_password_hash(password)
            update = "UPDATE SESSION_INFO SET pas_hash = (%s) WHERE USER_ID = (%s)"
            param = (hash,id)
            db.execute(update, param, 0)
            flash("Password changed!")
            # Redirect user to home page
            return redirect("/")
        else:
            app.logger.warning('%s In /account password did not match with confirmation password', username)
            flash("One or more fields filled incorrectly")
            return render_template("account.html", account_csv=account_csv[session["language"]], username=username.capitalize(), email=email, layout=layout[session["language"]])
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show them their account information
        id = session["user_id"]
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = (%s)"
        rows = db.execute(select, (id,), 1)
        username = rows[0]["user_name"]
        email = rows[0]["email"]

        return render_template("account.html", account_csv=account_csv[session["language"]], username=username.capitalize(), email=email, layout=layout[session["language"]])
################################################################################
################################ STATIC #####################################
###############################################################################
@app.route("/consent", methods=["GET", "POST"])
@language_check
def consent():
    """
    Consent form
    """
    language_set()
    if request.method == "POST":
        id = session["user_id"]
        if request.form.get("consent") == "on":
            update = f"UPDATE SESSION_INFO SET CONSENT=1 WHERE USER_ID = (%s)"
            db.execute(update, (id,), 0)
            select = "SELECT CONSENT FROM SESSION_INFO WHERE USER_ID = (%s)"
            rows = db.execute(select, (id,), 1)
            session['consent'] = rows[0]['consent']
        return redirect("/home")
    else:
        return render_template("consent.html", consent_csv=consent_csv[session["language"]], layout=layout[session["language"]])

@app.route("/eeg", methods=["GET", "POST"])
@language_check
def eeg():
    """
    EEG information
    """
    # If they clicked on the submit button
    if request.method == "POST":
        id = session["user_id"]
        # select the user info
        select = "SELECT * FROM SESSION_INFO WHERE USER_ID = (%s)"
        rows = db.execute(select, (id,), 1)

        # send_email with the users info to our server to contact them about participating
        message = 'Subject: EEG \n\n The following participant wants to participate in the EEG study' + '\n username: ' + str(rows[0]['user_name']) + "\n email: " + str(rows[0]['email']) + "\n user_id: " + str(rows[0]['user_id']) + "\n user_type: " + str(str(rows[0]['user_type']))
        email_sent = send_email(message, rows[0]['user_name'])
        # render a thank you page
        if email_sent:
            return render_template("sent_email.html", sent_email_csv=sent_email_csv[session["language"]], layout=layout[session["language"]])
        else:
            return render_template("email_unsent.html", email_unsent=email_unsent[session["language"]], layout=layout[session["language"]])
    else:
        language_set()
        return render_template("eeg.html", eeg_csv=eeg_csv[session["language"]], layout=layout[session["language"]])

@app.route("/home", methods=["GET", "POST"])
@login_required
@language_check
def home():
    """
    Home page, contains a money tab and a recommended task
    """
    # calculate the money earned to draw the barchart
    price = calculate_money()

    # make the recomendation system which will recommend one task, show only 1 div
    id = session["user_id"]
    # select all the completed tasks
    select = f"SELECT * FROM TASK_COMPLETED WHERE USER_ID = (%s)"
    rows = db.execute(select,(id,), 1)

    # select the user type to see if money barchart should be shown
    select = f"SELECT USER_TYPE FROM SESSION_INFO WHERE USER_ID = (%s)"
    user_type_row = db.execute(select,(id,), 1)
    # user type of 1 indicates they want and are able to participate for money
    if user_type_row[0]["user_type"] == 1:
        user_type = True
    # user type of 2 indicates they are unable to participate for money
    else:
        user_type = False
    recomendation = True
    # put the completed tasks in a list
    completed_tasks = []
    for i in rows:
        completed_tasks.append(i["task_id"])

    tasks[session["language"]]['corsi_title']
    # First recomendation is to do the phone survey
    if 5 not in completed_tasks or should_show_task(5):
        task = {"img":"/static/images/TaskIcons/phone_survey.png", "alt":"Phone survey", "title":tasks[session["language"]]['phone_survey_title'],  "text" : tasks[session["language"]]['phone_survey_description'], "link" : "/phone_survey", "button_text": tasks[session["language"]]['phone_survey_button']}
    # Second recomendation is to do the sf-36
    elif 4 not in completed_tasks or should_show_task(4):
        task = {"img":"/static/images/TaskIcons/SF-36.png", "alt":"sf_36", "title":tasks[session["language"]]['sf_36_title'],  "text" : tasks[session["language"]]['sf_36_description'], "link" : "/sf_36", "button_text": tasks[session["language"]]['sf_36_button']}
    # Third recomendation is to do corsi task
    elif  1 not in completed_tasks or should_show_task(1):
        task = {"img":"/static/images/TaskIcons/corsi.png", "alt":"corsi",  "title" : tasks[session["language"]]['corsi_title'], "text" : tasks[session["language"]]['corsi_description'], "link" : "/corsi", "button_text": tasks[session["language"]]['corsi_button']}
    # Fourth recomendation is to do n_back task
    elif 2 not in completed_tasks or should_show_task(2):
        task = {"img":"/static/images/TaskIcons/N-back.png", "alt":"N-back", "title" : tasks[session["language"]]['n_back_title'], "text" : tasks[session["language"]]['n_back_description'], "link" : "/n_back", "button_text": tasks[session["language"]]['n_back_button']}
    # Fifth recomendation is to do task switching task
    elif 3 not in completed_tasks or should_show_task(3):
        if session["language"] == "english":
            task = {"img":"/static/images/TaskIcons/TSwitch_EN.png", "alt":"task switching", "title" : tasks[session["language"]]['task_switching_title'], "text" : tasks[session["language"]]['task_switching_description'], "link" : "/task_switching", "button_text": tasks[session["language"]]['task_switching_button']}
        else:
            task = {"img":"/static/images/TaskIcons/TSwitch_NL.png", "alt":"task switching", "title" : tasks[session["language"]]['task_switching_title'], "text" : tasks[session["language"]]['task_switching_description'], "link" : "/task_switching", "button_text": tasks[session["language"]]['task_switching_button']}
    # If all tasks have been completed and are locked then give no recommendation dont show the div
    else:
        recomendation = False
        task = {"img":"", "alt":"", "title":"",  "text" : "", "link" : "", "button_text": ""}
    return render_template("home.html", price=price, user_type=user_type, recomendation=recomendation, layout=layout[session["language"]], home_csv=home_csv[session["language"]], img=task["img"], alt=task["alt"], title=task["title"], text=task["text"], link=task["link"], button_text=task["button_text"])


@app.route("/payment", methods=["POST", "GET"])
@login_required
@language_check
def payment():
    """
    payment
    """
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        IBAN = request.form.get("IBAN")
        address = request.form.get("address")
        collection = request.form.get("collection")
        id = session["user_id"]
        money_earned = calculate_money()
        # update the collection to 0 which means that the user has/will collect the money_earned
        # otherwise collect is 1
        date_collected = datetime.now()
        update = f"UPDATE TASK_COMPLETED SET COLLECT=0, DATE_COLLECTED = (%s) WHERE USER_ID = (%s)"
        db.execute(update, (date_collected, id), 0)

        # select the user info
        select = f"SELECT * FROM SESSION_INFO WHERE USER_ID = (%s)"
        rows = db.execute(select, (id,), 1)
        # send_email with the users info to our email to contact them about participating
        # email contains username, email, usertype, user_id and the ammount to be collect
        message = 'Subject: Payment collection \n\n The following participant wants to collect their payment for the study' + '\n username: ' + str(rows[0]['user_name']) + "\n First name: " + first_name + "\n Last name: " + last_name + "\n IBAN: " + IBAN + "\n Address: " + address +  "\n email: " + str(rows[0]['email']) + "\n user_id: " + str(rows[0]['user_id']) + "\n user_type: " + str(rows[0]['user_type']) + "\n ammount to collect: " + str(money_earned)
        email_sent = send_email(message, rows[0]['user_name'])

        if email_sent:
            # render a thank you page
            return render_template("collected.html", money_earned=money_earned, collected_csv=collected_csv[session["language"]], layout=layout[session["language"]])
        else:
            return render_template("email_unsent.html", email_unsent=email_unsent[session["language"]], layout=layout[session["language"]])
    else:
        return render_template("payment.html", payment=payment_csv[session["language"]], layout=layout[session["language"]])



@app.route("/about_study", methods=["GET"])
@language_check
def about_study():
    language_set()
    return render_template("about_study.html", about_study_csv=about_study_csv[session["language"]], layout=layout[session["language"]])

@app.route("/for_participant", methods=["GET"])
@language_check
def for_participant():
    language_set()
    return render_template("for_participant.html", for_participant_csv=for_participant_csv[session["language"]], layout=layout[session["language"]])

@app.route("/about_app", methods=["GET"])
@language_check
def about_app():
    language_set()
    return render_template("about_app.html", about_app_csv=about_app_csv[session["language"]], layout=layout[session["language"]])

@app.route("/contact", methods=["GET"])
@language_check
def contact():
    language_set()
    return render_template("contact.html", contact_csv=contact_csv[session["language"]], layout=layout[session["language"]])
port = int(os.getenv("PORT"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
