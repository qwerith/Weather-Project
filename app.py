import os
from flask import Flask, redirect, request, session, render_template, flash, url_for
from weather import get_weather
from accounts import Accounts, input_validation, login_required
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
secret_key = os.getenv("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("Flask secret key error")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secret_key
bcrypt = Bcrypt(app)


@app.route('/', methods=["GET", "POST"])
#@login_required
def index():
    if request.method == "POST" and request.form.get("location"):
        print(request.form.get("location"))
        location = request.form.get("location")
        DATA = get_weather(location)
        print(DATA)
        STATUS = f"{location} not found"
        return render_template('index.html', status=STATUS) if type(DATA) == RuntimeError else render_template("index.html", data=DATA) 
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = [request.form.get("username"), request.form.get("email"), request.form.get("password"), request.form.get("confirm_password")]
    if request.method == "POST" and all(char != "" for char in form):
        input_valid = input_validation(form[1:4])
        form.clear()
        if not input_valid == "":     
            flash(input_valid)
            return render_template("register.html")
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            flash(user.register(request.form.get("username")))
            return redirect(url_for("login"))
    else:
        form.clear()
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("email") != "" and request.form.get("password") != "":
        session.pop("user_id", None)
        input_valid = input_validation([request.form.get("email"), request.form.get("password")])
        if not input_valid == "":
            flash(input_valid)
            return render_template("login.html") 
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            user = user.login()
            if user:
                session["user_id"] = user[1][0][0]
                print(session["user_id"])
                return redirect("/")
            else:
                flash("An error occured")
                return render_template("login.html")        
    else:
        return render_template("login.html")

if __name__=="__main__":
    app.run()    