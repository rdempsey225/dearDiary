import os
import datetime
import flask
import werkzeug
import inspect
from werkzeug import security
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import date
from datetime import datetime
from helpers import apology, login_required, datefixer, get_line_number

#configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["datefixer"] = datefixer

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/ryandempsey/Documents/rdempsey225/project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
print(app.config['SQLALCHEMY_DATABASE_URI'])


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hash = db.Column(db.String(120), nullable=False)

class Entries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    entry = db.Column(db.Text, nullable=False)


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
    user_id = session.get("user_id")
    """Show home page with options to see or enter journal entry"""
    entries = Entries.query.filter_by(user_id=user_id).all()

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
        user = Users.query.filter_by(username=uname).first()

        # Ensure username doesn't already exist
        if user:
            return apology("username already exists", 400)

        # Generate Password Hash
        hash_pw = generate_password_hash(pword, method='pbkdf2:sha256', salt_length=16)

        # add user and hashed pw to db
        new_user = Users(username=uname, hash=hash_pw)
        db.session.add(new_user)
        db.session.commit()
    
    # check db to confirm user was added
       # usr = db.execute(
            #"SELECT * FROM users WHERE username = ?", uname
        #)

    # # Ensure username exists and password is correct
        #if len(usr) != 1:
            #return apology("registration failed", 403)

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
        uname = request.form.get("username")
        pword = request.form.get("password")
        # Ensure username was submitted
        if not uname:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not pword:
            return apology("must provide password", 403)

        # Query database for username
        user = Users.query.filter_by(username=uname).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, pword):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id

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
    print(f"entering entry route at line {get_line_number()}")
    # if reached via post, it means the user submitted request via ''button
    user_id = session.get("user_id")
    #store arguments of redirected from one of the history pages
    hist = request.args.get('hist')
   

    #capture today's date in date format for insertion sql
    now = datetime.now()
    entrydate = now.today()
    stringdate = entrydate
    print (f"capturing today's date at line {get_line_number()}",stringdate)

    #if redirected from an edit entry button, capture the values needed to revise entry in db
    wegot = request.form.get('editentry')

    if request.method == "POST":
        id = request.form.get("idedit")
        jentry = request.form.get("entry1")
        entrydate = request.form.get("entrydate")
        user = session.get("user_id")

        # ensure entry was entered
        if not jentry:
            return apology("Enter something into Journal", 400)
        if id and "id" not in id:
            print(f"ID received for editing at line {get_line_number()}: {id}")
            entry = Entries.query.filter_by(id=id).first()
            print(f"we got an entry to edit at line {get_line_number()}",entry)
            if entry:
                print(f"Entry found for editing at line {get_line_number()}:", entry)
                entry.entry = jentry
                entry.date = entrydate
                print(f"we got entry.entry at line {get_line_number()}",entry.entry, entry.date)
                db.session.commit()
                return redirect("/history")
            else:
                print(f"No entry found with that ID.line {get_line_number()}")
        # add new entry to entries table
        
        else:
            #otherwise, we create a new entry
            print(f"we are at line {get_line_number()} and neeed to create a new entry")
            new_entry = Entries(user_id=user_id, date=entrydate, entry=jentry)
            print(f"we created a new entry at line {get_line_number()}",new_entry)
            db.session.add(new_entry)
            db.session.commit()
            return redirect("/")
        
        # otherwise, check to see if a revision was submitted and save that revision
    else:
        id=''
        jentry=''
        entrydate = request.args.get('entrydate', datetime.now().strftime('%Y-%m-%d'))
        args=request.args.get('entryid')
        print(f"we are at the else statement at line {get_line_number()}",args)
        if 'entryid' in request.args:
            id = request.args.get('entryid')
            entry = Entries.query.filter_by(id=id).first()
            if entry:
                jentry = entry.entry
                entrydate = entry.date

        return render_template("entry.html",idedit=id,entrydate=stringdate,pentry=jentry,entry=jentry,dentry=jentry)

@app.route("/history", methods=["GET"])
@login_required
def history():
    user_id = session.get("user_id")
    #if routes were reached from modal on home page, args will be saved here
    args = request.args.get('historymodal')
    print(f"args for history at line {get_line_number()}", args)
    if not args:
        """unless route was reached from modal, show scrolly entries"""

        # get journal history
        entries = Entries.query.filter_by(user_id=user_id).all()
        print(f"we are in history app route line {get_line_number}",entries)

        if not entries:
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
        entries = Entries.query.filter_by(user_id=user_id).filter(
            db.extract('month', Entries.date) == monthvar,
            db.extract('year', Entries.date) == yearvar
        ).all()
        #return to entries page
    return render_template("entries.html", entries=entries)
@app.route("/scrollmy",methods=["GET"])
def scrollmy():
    #get user to perform query
    user_id = session.get("user_id")
    #if routes were reached from modal on home page, args will be saved here
    args = request.args.get('historymodal')
    print("args", args)
    if not args:
        """unless route was reached from modal, show scrolly entries"""

        # get journal history
        entries = Entries.query.filter_by(user_id=user_id).all()

        if len(entries) < 1:
            return apology("You don't have any entries yet", 400)
        # render scrolly history if history exists
        else:
            return render_template("scrollmy.html", entries=entries)
    return render_template("scrollmy.html")

# Ensure the application runs only if the script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
