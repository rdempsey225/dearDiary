import datetime
import requests
import flask
import inspect
from flask import redirect, render_template, session
from datetime import date
from datetime import datetime
from functools import wraps

def apology(message, code):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def datefixer(value):

    stringdate = datetime.strptime(value,'%Y-%m-%d')
    monthname = stringdate.strftime('%b')
    day = stringdate.strftime('%d')
    yr = stringdate.strftime('%Y')

    return f"{monthname+' '+day+','+' '+yr}"

def get_line_number():
    return inspect.currentframe().f_back.f_lineno