from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://theUserName:thePassword@localhost/mydb"
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

        query = f"SELECT username, password FROM users WHERE username='{userName}' AND password='{password}'"
        
        result = db.engine.execute(query)
        # user = result.fetchall()
        user = result.fetchone()

        if user:
            message = f"welcome, {user}"
        else:
            message = "Incorrect username or password"

    return render_template("login.html", message=message)


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


if __name__ == "__main__":
    # only for development
    app.run(debug=True)