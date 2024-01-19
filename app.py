import os
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect,render_template,request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from datetime import datetime
from helpers import apology, login_required, datefixer

#configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["datefixer"] = datefixer

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user = session.get("user_id")
    """Show home page with options to see or enter journal entry"""
    # get transaction history
    entries = db.execute(
        "SELECT id,date,entry AS 'jentry' FROM entries WHERE user_id = ?", user)

    if len(entries) < 1:
        return render_template("entry.html")
        #show animated home page with months and years to click on to see entries or enter new entries
    else:
        return render_template("hztimeline.html", entries=entries)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        uname = request.form.get("username")
        pword = request.form.get("password")
        cnf = request.form.get("confirmation")

    # Ensure username was submitted
        if not uname:
            return apology("must provide password", 400)

    # Ensure password was submitted
        elif not pword:
            return apology("must provide password", 400)

    # Ensure password confirmation was submitted
        elif not cnf:
            return apology("must confirm password", 400)

    # Ensure password and confirmation match
        elif pword != cnf:
            return apology("passwords don't match", 400)

    # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", uname)

    # Ensure username doesn't already exist
        if len(rows) != 0:
            return apology("username already exists", 400)

    # Generate Password Hash
        str = generate_password_hash(pword, method='pbkdf2', salt_length=16)

    # add user and hashed pw to db
        db.execute("INSERT INTO users (username,hash) VALUES(?,?)", uname, str)

    # check db to confirm user was added
        usr = db.execute(
            "SELECT * FROM users WHERE username = ?", uname
        )

    # # Ensure username exists and password is correct
        if len(usr) != 1:
            return apology("registration failed", 403)

    # redirect to home if user was added
        return redirect("/")

    # User reached route via GET (as by clicking the register link or being redirected from elsewhere)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/entry", methods=["GET", "POST"])
@login_required
def entry():
    """Log a journal entry """
    # if reached via post, it means the user submitted request via ''button

    #store arguments of redirected from one of the history pages
    hist = request.args.get('hist')

    #capture today's date in date format for insertion sql
    now = datetime.now()
    entrydate=now.today()
    stringdate = entrydate

    #if redirected from an edit entry button, capture the values needed to revise entry in db
    wegot=request.form.get('editentry')

    if request.method == "POST":
        id = request.form.get("idedit")
        jentry = request.form.get("entry1")
        entrydate = request.form.get("entrydate")
        user = session.get("user_id")

        # ensure entry was entered
        if not jentry:
            return apology("Enter something into Journal", 400)
        elif "id" not in id:
            db.execute("UPDATE entries SET entry = ? WHERE id = ?",jentry,id)
            return redirect("/history")
        # add new entry to entries table
        else:
            db.execute("INSERT INTO entries (user_id,date,entry) VALUES(?,?,?)",user, entrydate, jentry)

            return redirect("/")
        # otherwise, check to see if a revision was submitted and save that revision
    else:
        id=''
        jentry=''
        args=request.args.get('entryid')
        print("we are at the else statement",args)
        if args:
            id=args
            entry=db.execute("SELECT id,date,entry AS 'jentry' FROM entries WHERE id = ?", id)
            jentry=entry[0]["jentry"]
            stringdate=entry[0]["date"]
        elif not args:
            args=request.args.get('entrydate')
            if args:
                form=request.args.get('entrydate')
                stringdate = form
                print("hist", form)
            elif not args:
                print("there are no args")

        return render_template("entry.html",idedit=id,entrydate=stringdate,pentry=jentry,entry=jentry,dentry=jentry)

@app.route("/history", methods=["GET"])
@login_required
def history():
    user = session.get("user_id")
    #if routes were reached from modal on home page, args will be saved here
    args = request.args.get('historymodal')
    print("args", args)
    if not args:
        """unless route was reached from modal, show scrolly entries"""

        # get journal history
        entries = db.execute(
        "SELECT id,date,entry AS 'jentry' FROM entries WHERE user_id = ?", user)

        if len(entries) < 1:
            return apology("You don't have any entries yet", 400)
        # render scrolly history if history exists
        else:
            return render_template("entries.html", entries=entries)
        #if route was reached from  modal, show tabular list of entries instead
    else:
        #preparing date for query. This will show entries by month year selected from modal
        datevar=datetime.strptime(args,'%Y-%m-%d')
        monthvar=datevar.strftime('%m')
        yearvar=datevar.strftime('%Y')
        entries = db.execute(
        "SELECT id,date,entry AS 'jentry' FROM entries WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ? ",user,monthvar,yearvar)
        return render_template("entries.html", entries=entries)

@app.route("/scrollmy",methods=["GET"])
def scrollmy():
    #get user to perform query
    user = session.get("user_id")
    #if routes were reached from modal on home page, args will be saved here
    args = request.args.get('historymodal')
    print("args", args)
    if not args:
        """unless route was reached from modal, show scrolly entries"""

        # get journal history
        entries = db.execute(
        "SELECT id,date,entry AS 'jentry' FROM entries WHERE user_id = ?", user)

        if len(entries) < 1:
            return apology("You don't have any entries yet", 400)
        # render scrolly history if history exists
        else:
            return render_template("scrollmy.html", entries=entries)
    return render_template("scrollmy.html")
