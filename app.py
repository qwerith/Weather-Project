import os, re
from flask import Flask, redirect, request, session, render_template, flash, url_for
from weather import get_weather
from accounts import Accounts, input_validation, login_required
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv, find_dotenv
from mailing import send_gmail, day_of_week, set_up_track, compose_weather_mail_msg

load_dotenv(find_dotenv())
secret_key = os.getenv("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("Flask secret key error")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secret_key
bcrypt = Bcrypt(app)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST" and request.form.get("location"):
        print(request.form.get("location"))
        location = request.form.get("location")
        DATA = get_weather(location)
        STATUS = f"{location} not found"
        return render_template('index.html', status=STATUS) if type(DATA) == RuntimeError else render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass) 
    else:
        return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = [request.form.get("username"), request.form.get("email"), request.form.get("password"), request.form.get("confirm_password")]
    if request.method == "POST" and all(char != "" for char in form) and len(form[0]) < 20:
        input_valid = input_validation(form[1:4])
        form.clear()
        if not input_valid == []:     
            flash(input_valid, "info")
            return render_template("register.html")
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            flash(user.register(request.form.get("username")), "info")
            return redirect(url_for("login"))
    else:
        form.clear()
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form.get("email") != "" and request.form.get("password") != "":
        session.pop("user_id", None)
        input_valid = input_validation([request.form.get("email"), request.form.get("password")])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("login.html") 
        else:
            user = Accounts(request.form.get("email"), request.form.get("password"))
            user = user.user_verification()
            if user:
                session["user_id"] = user[1][0][0]
                session["username"] = user[1][0][1]
                session["email"] = user[1][0][2]    
                print(session["user_id"])
                return redirect("/")
            else:
                flash(["Wrong email or password"], "info")
                return render_template("login.html")        
    else:
        return render_template("login.html")


@login_required
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    return redirect("/")


@login_required
@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST" and request.form.get("password") != "":
        input_valid = input_validation([session["email"], request.form.get("password")])
        print(session["email"])
        if input_valid != []:
            print("test")
            flash(input_valid, "info")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user.delete()
            session.pop("user_id", None)
            return redirect("/")
        return redirect("/delete")
    return render_template("delete.html")


@login_required
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST" and request.form.get("password") != "":
        input_valid = input_validation([session["email"], request.form.get("password"),
        request.form.get("password_new"), request.form.get("password_new_confirm")])
        if input_valid != []:
            flash(input_valid, "info")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user.change_password(request.form.get("password_new"))
            return redirect("/")
        return redirect("/change_password")
    return render_template("change_password.html")


@login_required
@app.route("/track", methods=["POST"])
def track():
    filter = """['" ()]"""
    if request.method == "POST":
        # and session["track"] not in [None, request.form.get("location_id")]
        session.pop("track", None)
        location_name = re.sub(filter,"",request.form.get("location")).split(",")[0]
        location_id = re.sub(filter,"",request.form.get("location")).split(",")[1]
        print(location_name, location_id)
        session["track"] = location_id
        print(session["track"])
        DATA = get_weather(location_name)
        if set_up_track(session["user_id"], location_id) and type(DATA) != RuntimeError:
            send_gmail(compose_weather_mail_msg(DATA), session["email"])
        return ('', 204)
    return redirect("/")


def compass(direction):
    direction = int(direction)
    if direction > 135:
        direction = (direction - 135)
    elif direction < 135:
        direction = (135 - direction)
    return str(direction)
    
        
if __name__=="__main__":
    app.run()    