from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    userInput = ""
    if request.method == "POST":
        userInput = request.form.get("name", "")
    return render_template("about.html", userInput=userInput)



if __name__ == "__main__":
    app.run(debug=True)