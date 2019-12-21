from flask import Flask, redirect, render_template, request, session
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        new_password = request.form.get("confirmation")
        # ensure that all fiels were filled in correctly
        if not username:
            return apology("Fill in all fields")

        if check_password(password, new_password):
            # encrypt the users' password
            hash = generate_password_hash(password)

            # add user to the database
            #result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=username, hash=hash)
            #rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)

            # check if the username already existed
            #if not result:
            #    return apology("Username already in use")

            # log the user in
            #session["user_id"] = rows[0]["id"]
            session["user_id"] = 0

            # Redirect user to home page
            return redirect("/")
        else:
            return apology("One or more fields filled in incorrectly")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    #session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        #rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                  username=request.form.get("username"))

        # Ensure username exists and password is correct
        #if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #    return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        #session["user_id"] = rows[0]["id"]
        session["user_id"] = 0

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
