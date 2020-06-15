from flask import Flask, redirect, render_template, request, session, flash, jsonify,url_for
from flask_session import Session
from tempfile import mkdtemp
from db.postgresql import Db
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *
import re
from datetime import datetime, timedelta
import string
import random
import requests
import uuid
import json
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

app = Flask(__name__)
key  = open("secret_key.txt", "r")
secret_key = key.read()
app.secret_key = secret_key


# Ensure templates are auto-reloaded
#app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
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
forgot_password_csv = read_csv("static/csv/forgot_password.csv")
verify_csv = read_csv("static/csv/verify.csv")
reset_password_email = read_csv("static/csv/reset_password_email.csv")
youtube_csv = read_csv("static/csv/youtube.csv")
flash_msg_csv = read_csv("static/csv/flash_msg.csv")
admin_csv = read_csv("static/csv/admin.csv")
rec_system_csv = read_csv("static/csv/rec_system.csv")
rec_system_success_csv = read_csv("static/csv/rec_system_success.csv")

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

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)
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

def send_email(message, username, recipient_adress):
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
            server.sendmail(email, recipient_adress, message)
        return True
    except:
        print('fail')
        app.logger.info('%s tried to send the following email: %s. There was an error', username, message)
        return False

@app.route('/nortonsw_df670de0-523c-0.html', methods=["GET"])
def norton():
    return render_template("nortonsw_df670de0-523c-0.html")
################################################################################
##################### LINK TO CORSI TASK_ID = 0 ################################
###############################################################################
@app.route('/rt', methods=["GET"])
@language_check
@login_required
def rt():
    """
    This function manages the rt task.
    First it checks if it has been done already if it has it will automatically
    redirect user to the selected task.
    If the rt task of rt_long task has not been yet then it will check what task
    was chosen and select whether the rt or rt_long should be shown.
    Finally if there is a youtube video it will redirect the user to the video.
    If not it will redirect user to the task (rt or rt_long)
    """
    language = request.args.get('language')
    if language:
        return redirect("/home")

    id = session["user_id"]
    task = request.args.get('task')
    # select tasks that were completed that day by the user
    select = "SELECT * FROM task_completed WHERE user_id = (%s) AND task_id = (%s) AND date_trunc('day', time_exec) = date_trunc('day', current_date);"
    # check if the rt task has been completed
    rt_done = db.execute(select, (id,8), 1)
    #select = "SELECT * FROM task_completed WHERE user_id = (%s) AND task_id = (%s) AND date_trunc('day', time_exec) = date_trunc('day', current_date);"
    # check if the rt_long task has been completed
    #rt_long_done = db.execute(select, (id,9), 1)

    if session["language"] == "english":
        youtube_link_select = 'youtube_link'
    else:
        youtube_link_select = 'youtube_link_nl'
    # Check if either the short or long rt task has been done today already
    # If one of them has been done then redirect the user to the video of the selected task directly
    # They should not do the rt or rt_long again
    #if rt_done or rt_long_done:
    if rt_done or task == "task_switching":
        # select the youtube link to the video
        select = f'SELECT {youtube_link_select} FROM TASKS WHERE task_name=(%s)'
        youtube_link = db.execute(select,(task,), 1)
        task_link = '/' + task
        return render_template('youtube.html', youtube_csv=youtube_csv[session["language"]], youtube_link=youtube_link[0][0], task_link=task_link, layout=layout[session["language"]])

    # if the task is task_switching then the shortened RT is done
    # if it is not task switching the long rt is done

    #if task == "task_switching":
    # task_id for short rt = 8
    task_id = 8
    link = task_opening(task_id)
    task_link = link[0][0] + '&task=' + task + '&user_id=' + generate_id(id)
    print(task_link)
    select = f'SELECT {youtube_link_select} FROM TASKS WHERE task_id=(%s)'
    youtube_link = db.execute(select,(task_id,), 1)
    """
    else:
        # task_id for long rt = 9
        task_id = 9
        link = task_opening(task_id)
        task_link = link[0][0] + '&task=' + task + '&user_id=' + generate_id(id)
        print(task_link)
        select = f'SELECT {youtube_link_select} FROM TASKS WHERE task_id=(%s)'
        youtube_link = db.execute(select,(task_id,), 1)
    """
    # check if there is a youtube_link
    # if there is then redirect user to see the youtube video
    # if not redirect user to the task directly
    return render_template('youtube.html', youtube_csv=youtube_csv[session["language"]], youtube_link=youtube_link[0][0], task_link=task_link, layout=layout[session["language"]])


@app.route('/rt_end', methods=["GET"])
@language_check
@login_required
def rt_end():
    # get the task that was given as out variable
    # select the youtube link for the next task
    task = request.args.get('task')
    if session["language"] == "english":
        youtube_link_select = 'youtube_link'
    else:
        youtube_link_select = 'youtube_link_nl'
    select = f'SELECT {youtube_link_select} FROM TASKS WHERE task_name=(%s)'
    youtube_link = db.execute(select,(task,), 1)
    task_link = '/' + task

    # end the task
    #if task == "task_switching":
    task_id = 8
    task_completed(task_id)
    #else:
    #    task_id = 9
    #    task_completed(task_id)
    # check if there is a youtube_link
    # if there is then redirect user to see the youtube video
    # if not redirect user to the task directly
    if youtube_link[0][0]:
        return render_template('youtube.html', youtube_csv=youtube_csv[session["language"]], youtube_link=youtube_link[0][0], task_link=task_link, layout=layout[session["language"]])
    else:
        return redirect(task_link)



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

def calculate_rec_system_payment(f_promo_code):
    """
    This function calculates the reward/payment for referring friends to the study
    It takes the f_promo_code which is the promo code from the user that is logged in
    The user whose dashboard the payment will appear on.
    """
    total_payment = 0
    successful_completion = 0
    # select the number of times the user's promocode has been used
    # in the table this is stored as f_promo_code because the user at this point is the friend
    # make sure payment has not been collected already for this
    select = "SELECT * FROM rec_system where f_promo_code=(%s) AND COLLECT NOT IN ( 0 )"
    recomended = db.execute(select, (f_promo_code,), 1)
    # go over each person the user recommended
    for i in recomended:
        # since you only know this user's promo code select their info from SESSION_INFO
        # this is to check if they have been signed up for 1 year and have completed 12 tasks
      select = "SELECT user_id,time_sign_up FROM SESSION_INFO WHERE promo_code=(%s)"
      user_info = db.execute(select, (i["promo_code"],), 1)
      # get the date 1 year after the user has signed up
      today = datetime.now()
      one_year_after_sign_up = user_info[0]["time_sign_up"] + timedelta(weeks = 52)
      # if the user has been signed up for more than a year (52 weeks) then check if they
      # have completed 12 tasks.. if they have not then the total_payment is 0
      if one_year_after_sign_up < today:
        # select the number of tasks they have completed
        select = "SELECT * FROM TASK_COMPLETED WHERE user_id=(%s)"
        executed_tasks = db.execute(select, (user_info[0]["user_id"],), 1)
        # check if the number of tasks is more than 12 if so the referred friend has
        # successfully completed the study and the user may get the reward
        if len(executed_tasks) > 12:
            total_payment = total_payment + 5
            successful_completion = successful_completion + 1
    return (len(recomended),total_payment, successful_completion)

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
    all_tasks = db.execute(select_all_tasks, (id,), 1)

    # Assume that payment for task can be collected (because they have not collected payment this month yet)
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
                # (80-8)/(12*3) = 2
        if money_earned_tasks <= (80-8)/(12*3) and can_collect_task_this_month:
            money_earned = money_earned + money_earned_tasks
            # money_earned_tasks < 72. 72 is the total ammount a user can ever make on the tasks through the study
            # if money_earned_tasks is larger than 2 only count the first 2 euros for that month
        elif  money_earned_tasks > (80-8)/(12*3) and money_earned_tasks < 72 and can_collect_task_this_month:
            money_earned = money_earned + 2
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

        # check if 3 weeks has gone by after sign up. If its true then the survey is available to do
        select = "SELECT time_sign_up FROM SESSION_INFO WHERE user_id = (%s)"
        time_sign_up = db.execute(select, (session["user_id"],), 1)
        three_weeks_after_sign_up = time_sign_up[0][0] + timedelta(weeks=3)
        phone_survey_available = three_weeks_after_sign_up < datetime.now()
        calculate_money()
        return render_template("index.html", layout=layout[session["language"]], phone_survey_available=phone_survey_available, tasks=tasks[session["language"]], show_corsi=show_corsi, show_n_back=show_n_back, show_task_switching=show_task_switching, show_sf_36=show_sf_36, show_phone_survey=show_phone_survey)

################################################################################
################################ REGISTER #####################################
###############################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    preferred_language = "dutch"
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
        secret_recaptcha_r  = open("secret_recaptcha.txt", "r")
        secret_recaptcha = secret_recaptcha_r.read()
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'secret':secret_recaptcha, 'response': request.form.get("g-recaptcha-response")}

        # sending get request and saving the response as response object
        r = requests.get(url = URL, params = PARAMS)

        # extracting data in json format
        data = r.json()
        if not data["success"]:
            flash(flash_msg_csv[session["language"]]["robot"])
            return render_template("register.html", consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])


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
        f_promo_code_r = request.form.get("f_promo_code")

        # ensure that all fiels that are required were filled in correctly
        if not username_r or not birthdate_r or not gender_r or not email_r:
            flash(flash_msg_csv[session["language"]]["missing_fieds"])
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
        if f_promo_code_r:
            f_promo_code = f_promo_code_r.upper().replace(" ", "")

        # Check if password matches and has a number, capital letter, lower case letter and minimum 5 characters
        if check_password(password, new_password):
            # encrypt the users' password
            hash = generate_password_hash(password)

            # check if the username is already in use
            select = "SELECT user_name FROM SESSION_INFO WHERE user_name = (%s)"
            rows = db.execute(select, (username,), 1)
            # check true it means it is in use
            if rows:
                flash(flash_msg_csv[session["language"]]["used_email"])
                return render_template("register.html",   consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

            # send_email
            # select and delete a participation_id from the table with id's
            delete = """DELETE FROM participation_id WHERE p_id = ANY(SELECT * FROM participation_id order by p_id desc limit 1) RETURNING *"""
            # commit the delete statement by calling execute with fetch argument as 2
            participation_id_r = db.execute(delete, ("",), 2)
            # select the id from the list of lists
            participation_id = participation_id_r[0][0]
            session["participation_id"] = participation_id
            session["show_p_id"] = True

            # check if we have enough ID's left
            select = "SELECT * FROM PARTICIPATION_ID"
            all_p_ids = db.execute(select, ("", ), 1)

            # if there are less than 200 ID's then send a reminder email
            if len(all_p_ids) < 200:
                message = "Subject: (IMPORTANT) New Participation ID's Needed \n\n There are less than 200 participation_ids left."
                send_email(message, username, "agestudy@fsw.leidenuniv.nl")
            promo_code = add_promo_code_2_db()
            # add user to the database
            param = (username, email, gender, collect_possible, for_money, user_type, birthdate, hash, participation_id, promo_code)
            insert = "INSERT INTO session_info (user_name, email, gender, collect_possible, for_money, user_type, birthyear, pas_hash, participation_id, promo_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            result = db.execute(insert, param, 0)


            select = "SELECT * FROM SESSION_INFO WHERE user_name = %s"
            rows = db.execute(select, (username,), 1)
            # Remember which user has logged in
            session['user_id'] = rows[0][0]

            if f_promo_code_r:
                # if user has been recommended by a friend add promo code to db
                insert_promo_code = "INSERT INTO rec_system (user_id, promo_code, f_promo_code) VALUES (%s, %s, %s)"
                params = (session["user_id"], promo_code, f_promo_code)
                db.execute(insert_promo_code, params, 0)

            # send welcome email to paricipant and to agestudy with participants info
            message = 'Subject: New Participant \n\n username: ' + username + "\npsytoolkit_id: " + generate_id(session['user_id']) + "\n email: " + email + "\n user_id: " + str(rows[0][0]) + "\n user_type: " + str(user_type) + "\n gender: " + str(gender_r) + "\n language: " + session["language"] + "\n participation_id: " + participation_id + "\n Birthdate: " + birthdate
            send_email(message, username, "agestudy@fsw.leidenuniv.nl")
            subject_en='Welcome from Leiden University to Agestudy.nl (Important info, save the email)'
            subject_nl='Welkom van de Universiteit Leiden bij Agestudy.nl (Belangrijke info, bewaar deze e-mail)'
            send_direct_email(subject_en, subject_nl, email, subject_en, False, participation_id)

            # Redirect user to home page
            return redirect("/home")
        else:
            # the passwords did not match
            flash(flash_msg_csv[session["language"]]["unmatched_pas"])
            return render_template("register.html", consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        session["language"] = preferred_language
        language_set()
        return render_template("register.html",  consent_csv=consent_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

@app.route("/check_promo_code", methods=["GET"])
def check_promo_code():
    f_promo_code_r = request.args.get('f_promo_code')
    f_promo_code = f_promo_code_r.upper().replace(" ", "")
    select = "SELECT promo_code FROM SESSION_INFO WHERE promo_code = (%s)"
    rows = db.execute(select, (f_promo_code,), 1)
    return jsonify(len(rows) == 0)

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
    preferred_language = "dutch"
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
            flash(flash_msg_csv[session["language"]]["email_needed"])
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])
        # Ensure password was submitted
        elif not password:
            flash(flash_msg_csv[session["language"]]["pas_needed"])
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])

        # get the user information
        select = "SELECT * FROM SESSION_INFO WHERE user_name = (%s)"
        rows = db.execute(select, (username,), 1)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['pas_hash'], request.form.get("password")):
            flash(flash_msg_csv[session["language"]]["invalid_username"])
            if len(rows) != 1:
                app.logger.info('%s invalid username', username)
            else:
                app.logger.info('%s invalid password with email combination', username)
            return render_template("login.html", login_csv=login_csv[session["language"]], layout=layout[session["language"]])

        # Remember which user has logged in
        session['user_id'] = rows[0]['user_id']
        session['consent'] = rows[0]['consent']
        session['admin'] = rows[0]['admin']
        session['participation_id'] = rows[0]['participation_id']
        session['show_p_id'] = True
        session['show_rec_system'] = True
        select = "SELECT time_sign_up FROM SESSION_INFO WHERE user_id = (%s)"
        time_sign_up = db.execute(select, (session["user_id"],), 1)
        month_after_sign_up = time_sign_up[0][0] + timedelta(weeks=4)
        two_weeks_after_sign_up = time_sign_up[0][0] + timedelta(weeks=2)

        select_msg = f"SELECT * FROM BB_BOARD WHERE time_insert= (SELECT MAX(time_insert) FROM BB_BOARD WHERE USER_ID = (%s));"
        bb_board_selection = db.execute(select_msg, (rows[0]['user_id'],), 1)

        if month_after_sign_up < datetime.now() or bb_board_selection and bb_board_selection[0]["show_msg"]:
            session['show_p_id'] = False
        # user has been signed up for less than 2 weeks
        if two_weeks_after_sign_up > datetime.now():
            session['show_rec_system'] = False
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
    return len(password) >= 5 and number > 0


@app.route("/bb_board", methods=["GET", "POST"])
def bb_board():
    if request.method == "POST":
        # get the participation id and user id from the form
        participation_id =  request.form.get("participation_id_bb_board")
        user_id_bb_board = request.form.get("user_id_bb_board")
        # if the participation id was inserted then select the user id
        # set the variable user_id to be inserted in the db
        if participation_id:
            select = "SELECT user_id FROM SESSION_INFO WHERE participation_id=(%s)"
            user_id_selected = db.execute(select, (participation_id,), 1)
            user_id = user_id_selected[0][0]
        else:
            user_id = user_id_bb_board

        # If the user request to remove a message then set the show_msg variable to 0
        if request.form['msg'] == 'remove_msg':
            print("remove")
            update = "UPDATE BB_BOARD SET show_msg = 0 WHERE user_id = (%s)"
            db.execute(update, (user_id,), 0)
        # Else user requested to send a message to the user
        else:
            # Get the message and the message title
            bb_msg =  request.form.get("bb_msg")
            bb_msg_title =  request.form.get("bb_msg_title")

            # Insert the message in the database
            if user_id:
                insert = "INSERT INTO BB_BOARD(user_id, msg, msg_title, participation_id, show_msg) VALUES (%s, %s, %s, %s, %s);"
                inserted = db.execute(insert, (user_id, bb_msg, bb_msg_title, participation_id, 1), 0)
                # select the newest message inserted and if its the same as the message
                # That was sent via the form then the insertion was successful and flash that message
                select_msg = f"SELECT * FROM BB_BOARD WHERE time_insert= (SELECT MAX(time_insert) FROM BB_BOARD WHERE USER_ID = (%s));"
                bb_board_selection = db.execute(select_msg, (user_id,), 1)
                if bb_board_selection[0]["msg"] == bb_msg:
                    flash("Message saved")
                else:
                    flash("Message failed try again")
        return redirect("/admin")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    language_set()
    if request.method == "POST":
        email = request.form.get("email")
        select = "SELECT user_id FROM SESSION_INFO WHERE USER_NAME = (%s)"
        user_id = db.execute(select, (email.lower(),), 1)

        if user_id:
            # generate a random token
            token = str(uuid.uuid4())
            # generate a reset_id this will be used to find the row in the database
            reset_id = str(uuid.uuid4())
            # hash the token
            hash = generate_password_hash(token)

            # get the current time and the time 30 minutes after email request
            current_time = datetime.now()
            expiry_time = current_time + timedelta(minutes = 30)

            # add the values to the database
            # user_id, expiration time, hash and the reset_id
            insert = f"INSERT INTO RESET_PASSWORD (user_id, expiry_time, hash, reset_id) VALUES (%s, %s, %s, %s)"
            insert_values = (user_id[0][0], expiry_time, hash, reset_id)
            db.execute(insert, insert_values, 0)

            # save the reset_id in the session for later use
            session["reset_id"] = reset_id

            # get the root url (this case its https://www.agestudy.nl/)
            url_root = request.url_root
            # remove the last /
            url_root = url_root[:-1]
            s = 'https:'
            url_root = s + url_root.split(":")[1]
            # get the link for the reset with the token appended to it
            reset_link_url = url_for("reset_link", token=token)
            # combine the root and reset link together to form the final route
            url = url_root + reset_link_url
            subject = reset_password_email[session["language"]]['subject']
            msg_content = reset_password_email[session["language"]]['t1'] + '\n\n' + reset_password_email[session["language"]]['t2'] + '\n' + str(token + "\n\nLink: \n" + url) +  '\n\n\n' + reset_password_email[session["language"]]['expire']
            send_direct_email(subject, subject, email, msg_content, True, 0)

        return  redirect(url_for('verify'))
    else:
        return render_template("forgot_password.html", forgot_password_csv=forgot_password_csv[session["language"]], layout=layout[session["language"]])

def send_direct_email(subject_en, subject_nl, recipient_adress, msg_content, reset_password,participation_id):
    preferred_language = "dutch"
    if "language" in session:
        preferred_language = session["language"]

    if preferred_language == "english":
        subject = subject_en
        html_template = "automatic_welcome_encoded_en.htm"
    else:
        subject = subject_nl
        html_template = "automatic_welcome_encoded_nl.htm"

    msg = EmailMessage()
    msg.set_content(msg_content)
    msg['Subject'] = subject
    msg['From'] = 'admin@agestudy.nl'
    msg['To'] = recipient_adress.lower()
    msg.add_header('reply-to', 'agestudy@fsw.leidenuniv.nl')

    if not reset_password:
        asparagus_cid = make_msgid()
        msg.add_alternative(render_template(html_template, participation_id=participation_id).format(asparagus_cid=asparagus_cid[1:-1]), subtype='html')

    try:
        email_r  = open("email.txt", "r")
        email = email_r.read().strip('\n')
        pasw_r  = open("pass.txt", "r")
        pasw = pasw_r.read().strip('\n')
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
            server.login(email, pasw)
            server.send_message(msg)
    except:
        app.logger.info('%s tried to send the following email: %s. There was an error')

@app.route("/verify", methods=["GET", "POST"])
def verify():
    language_set()
    if request.method == "POST":
        token = request.form.get("token").strip(' ')

        select = "SELECT * FROM RESET_PASSWORD WHERE RESET_ID=(%s)"

        if "reset_id" in session:
            rows = db.execute(select, (session["reset_id"],), 1)
        else:
            flash(flash_msg_csv[session["language"]]["invalid_token"])
            return redirect("/forgot_password")

        if rows:
            expiry_time = rows[0]["expiry_time"]
            if expiry_time > datetime.now():
                # the token has not expired yet
                hash = rows[0]["hash"]
                # check if the token is the correct one
                # If it is then redirect user to reset page
                if check_password_hash(hash,token):
                    return redirect("/reset")
                # If it is not then let them request a new one again
                else:
                    flash(flash_msg_csv[session["language"]]["invalid_token"])
                    return redirect("/forgot_password")
            else:
                #the token has expired
                flash(flash_msg_csv[session["language"]]["expired_token"])
                return redirect("/forgot_password")
        else:
            #the token has expired
            flash(flash_msg_csv[session["language"]]["invalid_token"])
            return redirect("/forgot_password")
    else:
        return render_template("verify.html", verify_csv=verify_csv[session["language"]], layout=layout[session["language"]])


@app.route("/reset", methods=["GET", "POST"])
def reset():
    language_set()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        select = "SELECT * FROM RESET_PASSWORD WHERE RESET_ID=(%s)"
        if "reset_id" in session:
            password_reset_rows = db.execute(select, (session["reset_id"],), 1)
        else:
            flash(flash_msg_csv[session["language"]]["incorrect_route"])
            return redirect("/forgot_password")

        if password_reset_rows:
            user_id=password_reset_rows[0][0]
            print(user_id)
        else:
            flash(flash_msg_csv[session["language"]]["invalid_token"])
            return redirect("/forgot_password")

        # check if the new password is properly implemented
        if check_password(password, confirmation):
            # encrypt the users' password
            hash = generate_password_hash(password)
            update = "UPDATE SESSION_INFO SET pas_hash = (%s) WHERE USER_ID = (%s)"
            param = (hash,user_id)
            db.execute(update, param, 0)
            flash(flash_msg_csv[session["language"]]["change_pas"])
            # Redirect user to home page
            return redirect("/login")
        else:
            app.logger.warning('%s In /reset password did not match with confirmation password', user_id)
            flash(flash_msg_csv[session["language"]]["unmatched_pas"])
            return redirect("/forgot_password")
    else:
        return render_template("reset.html", account_csv=account_csv[session["language"]], register_csv=register_csv[session["language"]], layout=layout[session["language"]])

@app.route("/reset_link", methods=["GET"])
def reset_link():
    language_set()
    token = request.args["token"]
    select = "SELECT * FROM RESET_PASSWORD WHERE RESET_ID=(%s)"
    if "reset_id" in session:
        rows = db.execute(select, (session["reset_id"],), 1)
    else:
        flash(flash_msg_csv[session["language"]]["invalid_token"])
        return redirect("/forgot_password")

    if rows:
        expiry_time = rows[0]["expiry_time"]
        if expiry_time > datetime.now():
            # the token has not expired yet
            hash = rows[0]["hash"]
            # check if the token is the correct one
            # If it is then redirect user to reset page
            if check_password_hash(hash,token):
                return redirect("/reset")
            # If it is not then let them request a new one again
            else:
                flash(flash_msg_csv[session["language"]]["invalid_token"])
                return redirect("/forgot_password")
        else:
            #the token has expired
            flash(flash_msg_csv[session["language"]]["expired_token"])
            return redirect("/forgot_password")
    else:
        #the token has expired
        flash(flash_msg_csv[session["language"]]["invalid_token"])
        return redirect("/forgot_password")

    return redirect("/login")

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
            flash(flash_msg_csv[session["language"]]["incorrect_pas"])
            app.logger.warning('%s Tried to change password in the /account but old password was incorrect', username)
            return render_template("account.html", account_csv=account_csv[session["language"]], username=username.capitalize(), email=email, layout=layout[session["language"]])
        # check if the new password is properly implemented
        if check_password(password, confirmation):
            # encrypt the users' password
            hash = generate_password_hash(password)
            update = "UPDATE SESSION_INFO SET pas_hash = (%s) WHERE USER_ID = (%s)"
            param = (hash,id)
            db.execute(update, param, 0)
            flash(flash_msg_csv[session["language"]]["change_pas"])
            # Redirect user to home page
            return redirect("/")
        else:
            app.logger.warning('%s In /account password did not match with confirmation password', username)
            flash(flash_msg_csv[session["language"]]["incorrect_fields"])
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
        message = 'Subject: EEG \n\n The following participant wants to participate in the EEG study' + '\n username: ' + str(rows[0]['user_name']) + "\n email: " + str(rows[0]['email']) + "\n user_id: " + str(rows[0]['user_id']) + "\n user_type: " + str(str(rows[0]['user_type'])) + "\n language: " + session["language"]
        email_sent = send_email(message, rows[0]['user_name'], "agestudy@fsw.leidenuniv.nl")
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

    # make the recomendation system which will recommend one task, show only 1 div
    id = session["user_id"]

    select = "SELECT promo_code FROM SESSION_INFO WHERE USER_ID=(%s)"
    f_promo_code = db.execute(select, (id,), 1)
    # calculate the money earned to draw the barchart
    task_payment = calculate_money()
    rec_system_payment = calculate_rec_system_payment(f_promo_code[0][0])
    price = task_payment + rec_system_payment[1]

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

    select = "SELECT time_sign_up FROM SESSION_INFO WHERE user_id = (%s)"
    time_sign_up = db.execute(select, (session["user_id"],), 1)
    three_weeks_after_sign_up = time_sign_up[0][0] + timedelta(weeks=3)
    phone_survey_available = three_weeks_after_sign_up < datetime.now()


    one_year_after_sign_up = time_sign_up[0][0] + timedelta(weeks=52)
    select = "SELECT next_collection from TASK_COMPLETED WHERE user_id = (%s)"
    next_collection = db.execute(select, (session["user_id"],), 1)
    can_collect_payment = False
    if one_year_after_sign_up < datetime.now() and next_collection[0][0] and next_collection[0][0] < datetime.now():
        can_collect_payment = True

    select_msg = f"SELECT * FROM BB_BOARD WHERE time_insert= (SELECT MAX(time_insert) FROM BB_BOARD WHERE USER_ID = (%s));"
    bb_board_selection = db.execute(select_msg, (id,), 1)
    bb_msg=""
    bb_msg_title=""
    if bb_board_selection and bb_board_selection[0]["show_msg"]:
        bb_msg = bb_board_selection[0]["msg"]
        bb_msg_title = bb_board_selection[0]["msg_title"]
        bb_no_msg = False
    else:
        bb_no_msg = True

    # First recomendation is to do the phone survey
    if (5 not in completed_tasks or should_show_task(5)) and phone_survey_available:
        task = {"img":"/static/images/TaskIcons/phone_survey.png", "alt":"Phone survey", "btn_class": "survey", "title":tasks[session["language"]]['phone_survey_title'],  "text" : tasks[session["language"]]['phone_survey_description'], "link" : "/phone_survey", "button_text": tasks[session["language"]]['phone_survey_button']}
    # Second recomendation is to do the sf-36
    elif 4 not in completed_tasks or should_show_task(4):
        task = {"img":"/static/images/TaskIcons/SF-36.png", "alt":"Health survey", "btn_class": "survey", "title":tasks[session["language"]]['sf_36_title'],  "text" : tasks[session["language"]]['sf_36_description'], "link" : "/sf_36", "button_text": tasks[session["language"]]['sf_36_button']}
    # Third recomendation is to do corsi task
    elif  1 not in completed_tasks or should_show_task(1):
        task = {"img":"/static/images/TaskIcons/corsi.png", "alt":"Pattern Memory", "btn_class":"", "title" : tasks[session["language"]]['corsi_title'], "text" : tasks[session["language"]]['corsi_description'], "link" : "/rt?task=corsi", "button_text": tasks[session["language"]]['corsi_button']}
    # Fourth recomendation is to do n_back task
    elif 2 not in completed_tasks or should_show_task(2):
        task = {"img":"/static/images/TaskIcons/N-back.png", "alt":"Letter Memory",  "btn_class":"", "title" : tasks[session["language"]]['n_back_title'], "text" : tasks[session["language"]]['n_back_description'], "link" : "/rt?task=n_back", "button_text": tasks[session["language"]]['n_back_button']}
    # Fifth recomendation is to do task switching task
    elif 3 not in completed_tasks or should_show_task(3):
        if session["language"] == "english":
            task = {"img":"/static/images/TaskIcons/TSwitch_EN.png", "alt":"Task Switching",  "btn_class":"", "title" : tasks[session["language"]]['task_switching_title'], "text" : tasks[session["language"]]['task_switching_description'], "link" : "/rt?task=task_switching", "button_text": tasks[session["language"]]['task_switching_button']}
        else:
            task = {"img":"/static/images/TaskIcons/TSwitch_NL.png", "alt":"Task Switching", "btn_class":"", "title" : tasks[session["language"]]['task_switching_title'], "text" : tasks[session["language"]]['task_switching_description'], "link" : "/rt?task=task_switching", "button_text": tasks[session["language"]]['task_switching_button']}
    # If all tasks have been completed and are locked then give no recommendation dont show the div
    else:
        recomendation = False
        task = {"img":"", "alt":"", "title":"", "btn_class":"",  "text" : "", "link" : "", "button_text": ""}
    return render_template("home.html", len_rec_system_payment=rec_system_payment[0], suc_rec_system=rec_system_payment[2], bb_no_msg=bb_no_msg, bb_msg_title=bb_msg_title, bb_msg=bb_msg, price=price, can_collect_payment=can_collect_payment, user_type=user_type, recomendation=recomendation, layout=layout[session["language"]], home_csv=home_csv[session["language"]], btn_class=task["btn_class"], img=task["img"], alt=task["alt"], title=task["title"], text=task["text"], link=task["link"], button_text=task["button_text"])

@app.route("/rec_system", methods=["GET", "POST"])
@login_required
@language_check
def rec_system():
    select = "SELECT promo_code FROM SESSION_INFO WHERE USER_ID=(%s)"
    promo_code = db.execute(select, (session["user_id"],), 1)
    if request.method == "POST":
        f_promo_code_r = request.form.get("f_promo_code")
        f_promo_code = f_promo_code_r.upper().replace(" ", "")
        if f_promo_code != promo_code[0][0]:
            insert = "INSERT INTO rec_system (user_id, promo_code, f_promo_code, collect) VALUES (%s, %s, %s, %s)"
            params = (session["user_id"], promo_code[0][0], f_promo_code, 1)
            db.execute(insert, params, 0)
            return render_template("rec_system_success.html", rec_system_success_csv=rec_system_success_csv[session["language"]], layout=layout[session["language"]])
        else:
            flash(flash_msg_csv[session["language"]]["same_promo_code"])
            return redirect("/rec_system")
    else:
        select = "SELECT promo_code FROM rec_system WHERE promo_code = (%s)"
        rows = db.execute(select, (promo_code[0][0],), 1)
        show_rec_system_form = (len(rows) == 0)
        return render_template("rec_system.html", show_rec_system_form=show_rec_system_form, promo_code=promo_code[0][0], layout=layout[session["language"]], rec_system_csv=rec_system_csv[session["language"]] )

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
        task_payment = calculate_money()
        # update the collection to 0 which means that the user has/will collect the money_earned
        # otherwise collect is 1
        date_collected = datetime.now()
        next_collection = datetime.now() + timedelta(weeks = 52)
        update = f"UPDATE TASK_COMPLETED SET COLLECT=0, DATE_COLLECTED = (%s), next_collection = (%s) WHERE USER_ID = (%s)"
        db.execute(update, (date_collected, next_collection, id), 0)

        # select the user info
        select = f"SELECT * FROM SESSION_INFO WHERE USER_ID = (%s)"
        rows = db.execute(select, (id,), 1)

        # if the payment has already been collected by friend then make sure friend does not see payment again
        # collect = 0 if it has been collected and 1 otherwise
        f_promo_code = rows[0]["promo_code"]
        rec_system_payment = calculate_rec_system_payment(f_promo_code)

        update = f"UPDATE rec_system SET COLLECT=0 WHERE f_promo_code = (%s)"
        db.execute(update, (f_promo_code,), 0)

        money_earned = task_payment + rec_system_payment[1]
        # send_email with the users info to our email to contact them about participating
        # email contains username, email, usertype, user_id and the ammount to be collect
        message = 'Subject: Payment collection \n\n The following participant wants to collect their payment for the study' + '\n username: ' + str(rows[0]['user_name']) + "\n First name: " + first_name + "\n Last name: " + last_name + "\n IBAN: " + IBAN + "\n Address: " + address +  "\n email: " + str(rows[0]['email']) + "\n user_id: " + str(rows[0]['user_id']) + "\n user_type: " + str(rows[0]['user_type']) + "\n ammount to collect: " + str(money_earned) + "\n language: " + session["language"]
        email_sent = send_email(message, rows[0]['user_name'], "agestudy@fsw.leidenuniv.nl")

        if email_sent:
            # render a thank you page
            return render_template("collected.html", money_earned=money_earned, collected_csv=collected_csv[session["language"]], layout=layout[session["language"]])
        else:
            return render_template("email_unsent.html", email_unsent=email_unsent[session["language"]], layout=layout[session["language"]])
    else:
        return render_template("payment.html", payment=payment_csv[session["language"]], layout=layout[session["language"]])

@app.route("/admin", methods=["POST", "GET"])
@login_required
@language_check
def admin():
    """
    This function controls the admin page, a page which gives an overview of the database.
    It also allows changes of the database
    """
    if session["admin"] != 1:
        return redirect("/home")

    return render_template("admin.html", admin_csv=admin_csv[session["language"]], layout=layout[session["language"]])

@app.route("/select_user", methods=["GET"])
@language_check
def select_user():
    username = request.args.get('username').lower()
    user_id = request.args.get('user_id').lower()
    participation_id = request.args.get('participation_id').lower()

    if username:
        # get the user information
        select = """SELECT "user_id", "email", "gender",
                           "birthyear", "user_type",
                           "participation_id", "time_sign_up",
                           "admin"
                   FROM SESSION_INFO WHERE user_name  = (%s)"""
        rows = db.execute(select, (username,), 1)
    if user_id:
        select = """SELECT "user_id", "email", "gender",
                           "birthyear", "user_type",
                           "participation_id", "time_sign_up",
                           "admin"
                   FROM SESSION_INFO WHERE user_id  = (%s)"""
        rows = db.execute(select, (user_id,), 1)
    if participation_id:
        select = """SELECT "user_id", "email", "gender",
                           "birthyear", "user_type",
                           "participation_id", "time_sign_up",
                           "admin"
                   FROM SESSION_INFO WHERE participation_id  = (%s)"""
        rows = db.execute(select, (participation_id,), 1)
    user = {}
    if rows:
        user = {'user_id':rows[0]["user_id"], 'email':rows[0]["email"], 'gender':rows[0]["gender"],
                'birthdate':rows[0]["birthyear"], 'user_type': rows[0]["user_type"],
                'participation_id': rows[0]["participation_id"],
                'time_sign_up': rows[0]['time_sign_up'], 'admin': rows[0]['admin'],
                'psytoolkit_id': generate_id(rows[0]["user_id"])}
    return jsonify(user)

@app.route("/query_data", methods=["GET"])
@language_check
def query_data():
    # gender
    gender_r = request.args.get('gender').lower()
    gender = preprocess_gender(gender_r)
    select = """SELECT "user_id", "email", "gender",
                       "birthyear", "user_type",
                       "participation_id", "time_sign_up",
                       "admin"
               FROM SESSION_INFO WHERE gender = (%s)"""
    rows = db.execute(select, (gender,), 1)

    #User type
    user_type = request.args.get('user_type')
    print(user_type)
    return jsonify(rows)

@app.route("/get_data", methods=["GET"])
@language_check
def get_data():
    select = "SELECT * FROM SESSION_INFO"
    all_participants = db.execute(select, (""), 1)
    df_all_p = pd.DataFrame(all_participants)
    df_all_p = df_all_p.rename(columns={0: "user_id", 1: "user_name", 2:"email", 3:"gender", 4:"collect_possible",
    5:"for_money", 6:"user_type", 7:"birthyear", 8: "pas_hash", 9: "consent", 10:"time_sign_up",
    11:"participation_id", 12:"admin"})

    # num of participants
    num_p = len(df_all_p)
    # average age participants
    # change the birthyear type to integer
    df_all_p["date"] = pd.to_datetime(df_all_p.birthyear).values.astype(int)
    # get the mean birthyear
    average_year = pd.to_datetime(df_all_p["date"].mean())
    df_all_p["year"] = df_all_p["birthyear"].apply(lambda x: x.year)
    # age quantiles
    year_summary = df_all_p["year"].describe()
    q1 = year_summary.loc['25%']
    q3 = year_summary.loc['75%']
    iqr = q3 - q1
    lower_bound = q1 -(1.5 * iqr)
    outliers = list(df_all_p[df_all_p["year"] < lower_bound].groupby(by=["year"]).groups.keys())
    quantiles_summary = {"q1": q1, "median": year_summary.loc['50%'], "q3": q3,
                        "lower_bound": lower_bound, "min": year_summary.loc['min'],
                        "max": year_summary.loc['max'], "outliers": outliers}

    # user_type statistics
    count_user_type1 = df_all_p.groupby(by="user_type").size().loc[1]
    count_user_type2 = df_all_p.groupby(by="user_type").size().loc[2]
    user_type_mode = df_all_p["user_type"].mode()[0]
    user_type = [{"user_type":"paid", "value": int(count_user_type1)}, {"user_type":"unpaid", "value": int(count_user_type2)}]

    # gender statistics
    male = df_all_p.groupby(by="gender").size().loc[1]
    female = df_all_p.groupby(by="gender").size().loc[2]
    gender_mode = df_all_p[df_all_p["gender"] != 999]["gender"].mode()[0]
    gender = [{"gender":"male", "value": int(male)},{"gender": "female", "value":int(female)}]

    # basic stats
    basic_stats = {"num_p": int(num_p), "average_year": str(average_year), "quantiles_summary": quantiles_summary,
                    "user_type": user_type, "user_type_mode": int(user_type_mode),
                    "gender":gender, "gender_mode": int(gender_mode)}
    # basic stats contains basic information
    select = "SELECT * FROM TRACKED_TASK"
    tracked_task = db.execute(select, ("", ), 1)
    tracked_task_df = pd.DataFrame(tracked_task)
    tracked_task_df = tracked_task_df.rename(columns={0:"time_exec", 1:"user_id", 2:"task_id",3:"status"})
    merged = df_all_p.merge(tracked_task_df, on='user_id')
    merged["month"] = merged["time_exec"].apply(lambda x: x.month)


    tasks = task_frequency(merged)
    total_money_dict = total_money(merged)
    projected_money_dict = projected_money(num_p)

    bullet_data = [
  {
    "title":"Commited payment",
    "subtitle":"euros",
    "ranges":[total_money_dict["rt"],total_money_dict["survey"],total_money_dict["total"]],
    "measures":[total_money_dict["tasks"]],
    "markers":[0]
  },
  {
    "title":"Projected payment",
    "subtitle":"euros",
    "ranges":[projected_money_dict["rt"],projected_money_dict["survey"],projected_money_dict["total"]],
    "measures":[projected_money_dict["tasks"]],
    "markers":[0]
  }
]

    merged["time_sign_up"] = pd.to_datetime(merged["time_sign_up"])
    by_id_month = merged.groupby(by = ["user_id", "month"])
    active = get_num_active_participants(by_id_month)
    basic_stats["num_active_p"] = active

    merged["year_exec"] = merged["time_exec"].apply(lambda x: x.year)
    merged["day_exec"] = merged["time_exec"].apply(lambda x: x.day)
    merged["time_exec_ymd"] = merged.apply(lambda row: str(row.year_exec) + "-" + str(row.month) + "-" + str(row.day_exec), axis=1)
    streamgraph_df = merged[['time_exec_ymd','task_id', 'status']]
    streamgraph_df = streamgraph_df[streamgraph_df['status'] == 1]
    streamgraph_pivot = streamgraph_df.pivot_table(index='time_exec_ymd', columns='task_id',
                        aggfunc=len, fill_value=0)
    flattened_streamgraph = pd.DataFrame(streamgraph_pivot.to_records())
    flattened_streamgraph = flattened_streamgraph.rename(columns={"('status', 1)": "corsi", "('status', 2)":"n_back", "('status', 3)":"t_switch",
                          "('status', 4)":"sf_36", "('status', 5)":"phone_survey", "('status', 8)":"rt" })
    #flattened_streamgraph = flattened_streamgraph.set_index('time_exec_ymd')
    streamgraph_data = flattened_streamgraph.to_json(orient="records")

    merged["time_sign_up"] = pd.to_datetime(merged["time_sign_up"])
    merged["year_sign_up"] = merged["time_sign_up"].apply(lambda x: x.year)
    merged["day_sign_up"] = merged["time_sign_up"].apply(lambda x: x.day)
    merged["month_sign_up"] = merged["time_sign_up"].apply(lambda x: x.month)
    merged["time_sign_up_ymd"] = merged.apply(lambda row: str(row.year_sign_up) + "-" + str(row.month_sign_up) + "-" + str(row.day_sign_up), axis=1)
    sign_up_df = merged[['status','time_sign_up_ymd']]
    sign_up_data = sign_up_df.groupby(by="time_sign_up_ymd").count()
    flattened_sign_up = pd.DataFrame(sign_up_data.to_records())
    sign_up = flattened_sign_up.to_json(orient="records")

    data = {"basic_stats": basic_stats, "tasks": tasks, "bullet": bullet_data, "streamgraph_data": streamgraph_data, "sign_up": sign_up }
    data_json = json.dumps(data)
    return data_json

@app.route("/inactive_users", methods=["GET"])
@language_check
def inactive_users():
    select = "SELECT * FROM SESSION_INFO"
    all_participants = db.execute(select, (""), 1)
    df_all_p = pd.DataFrame(all_participants)
    df_all_p = df_all_p.rename(columns={0: "user_id", 1: "user_name", 2:"email", 3:"gender", 4:"collect_possible",
    5:"for_money", 6:"user_type", 7:"birthyear", 8: "pas_hash", 9: "consent", 10:"time_sign_up",
    11:"participation_id", 12:"admin"})

    # basic stats contains basic information
    select = "SELECT * FROM TASK_COMPLETED"
    task_completed = db.execute(select, ("", ), 1)
    task_completed_df = pd.DataFrame(task_completed)
    task_completed_df = task_completed_df.rename(columns={0:"time_exec", 1:"user_id", 2:"task_id",3:"status"})

    sign_up_1_month_ago = datetime.now() - timedelta(weeks = 4)
    # participants who have been signed up for over a month
    p_signed_up_1_month_ago = set(df_all_p[df_all_p["time_sign_up"] < sign_up_1_month_ago]["user_id"].unique())
    # participants who have performed tasks (not including surveys)
    p_who_performed_tasks = set(task_completed_df["user_id"].unique())

    # participants who signed up more than a month ago and hasnt performed any tasks
    non_active_users = p_signed_up_1_month_ago - p_who_performed_tasks
    print(non_active_users)
    # participants_id of these non_active_users
    inactive_users_p_id = df_all_p[df_all_p['user_id'].isin(non_active_users)]["participation_id"]
    inactive_users_df = df_all_p[df_all_p['user_id'].isin(non_active_users)]
    inactive_users = inactive_users_df[["user_id", "participation_id"]]
    inactive_users_list = inactive_users.to_json(orient="records")
    print(inactive_users_list)
    return inactive_users_list

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

#port = int(os.getenv("PORT"))

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=port)
