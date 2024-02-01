from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://myuser:kali@localhost/mydb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    userInput = ""
    if request.method == "POST":
        userInput = request.form.get("name", "")
    return render_template("about.html", userInput=userInput)

@app.route("/login", methods=["GET", "POST"])
def signup():
    message = ""
    if request.method == "POST":
        userName = request.form.get("userName")
        password = request.form.get("password")

        query = f"SELECT user_id, username, password FROM users WHERE username='{userName}' AND password='{password}'"
        
        result = db.engine.execute(query)
        # user = result.fetchall()
        user = result.fetchone()

        if user:
            return redirect(url_for("welcome", user_id = user[0]))
        else:
            message = "Incorrect username or password"

    return render_template("login.html", message=message)

@app.route("/welcome/<int:user_id>", methods=["GET"])
def welcome(user_id):
    query = f"select username from users where user_id={user_id}"

    result = db.engine.execute(query)
    user = result.fetchone()

    if user:
        return f"welcome, {user[0]}, you are logged in"
    else:
        return "user not found"
    
def blackList(string):
    badChars = ["'", ";", "--"]
    for char in badChars:
        if char in string.lower():
            return True
    return False

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        userName = request.form.get("userName")
        password = request.form.get("password")

        if blackList(userName):
            message = "not valid"
            return render_template("register.html", message = message)

        existanceQuery = "SELECT username FROM users WHERE username=%s"
        userExists = db.engine.execute(existanceQuery, (userName)).fetchone()

        if userExists:
            message = "username already exists"
        else:
            insertQuery = "insert into users (username, password) values (%s, %s)"
            db.engine.execute(insertQuery, (userName, password))
            message = "Registration was successful"

    return render_template("register.html", message=message)

@app.route("/redirect", methods=["GET"])
def redirecting():
    return render_template("redirect.html")

@app.route("/open", methods=["GET"])
def open():
    # getting url value from the url of the page
    targetUrl = request.args.get("url")
    # if action exists use that else defaults to "redirect"
    action = request.args.get("action", "redirect")

    # open redirection
    if action == "redirect":
        return redirect(targetUrl)
    
    # SSRF
    elif action == "fetch":
        try:
            response = requests.get(targetUrl, timeout = 5)

            if response.status_code == 200:
                return f"received ok, {targetUrl}"
            else:
                return f"received {response.status_code} from {targetUrl}"
            
        except requests.ConnectionError:
            return f"conncection refused by {targetUrl}"
        
        except requests.Timeout:
            return f"connection timed out by {targetUrl}"
        
        except Exception as error:
            return str(error)

    return "specify action and url"

if __name__ == "__main__":
    # only for development
    app.run(debug=True)