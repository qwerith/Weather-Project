import os, re
from flask import Flask, redirect, request, session, render_template, flash, url_for
from weather import get_weather
from accounts import Accounts, input_validation, login_required, generate_temporary_password
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv, find_dotenv
from mailing import send_gmail, day_of_week, set_up_track, compose_weather_mail_msg, stop_tracking, compose_recovery_mail_msg

temp_storage = []
location_list = [{"search_0" : False}, {"search_1" : False}, {"search_2" : False}]
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
        location = request.form.get("location").capitalize()
        print(location)
        DATA = get_weather(location)
        STATUS = f"{location} not found"
        if type(DATA) != RuntimeError:
            search_result = Quick_search.create_quick_search(location, location_list)
            if session.get("user_id") != None:
                print(search_result)
                Quick_search.write_quick_search_buffer(search_result)
                search_result = Quick_search.query_quick_search()
            else:
                search_result = {"Unknown" : search_result}
        return render_template('index.html', status=STATUS) if type(DATA) == RuntimeError else render_template("index.html", data=DATA, day_of_week = day_of_week,
         compass=compass, search_result=search_result) 
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
    Quick_search.clear_buffer()
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
            return render_template("delete.html")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user.delete()
            Quick_search.clear_buffer()
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
            return render_template("change_password.html")
        user = Accounts(session["email"], request.form.get("password"))
        if user.user_verification():
            user.change_password(request.form.get("password_new"))
            return redirect("/")
        return redirect("/change_password")
    return render_template("change_password.html")


@app.route("/restore_password", methods=["GET", "POST"])
def restore_password():
    if request.method == "POST":
        input_valid = input_validation([session.get("recovery_email"), request.form.get("temp_passsword"), request.form.get("password_new"), request.form.get("password_new_confirm")])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("restore_password.html")
        temp_password_hash = session.get("temporary_password_hash")
        if temp_password_hash:
            user = Accounts(session.get("recovery_email"), request.form.get("password_new"))
            session.pop("recovery_email", None)
            session.pop("temporary_password_hash", None)
            if not user.restore_password(temp_password_hash, request.form.get("temp_passsword")):
                return redirect("/restore_password.html")
            return redirect("/login")
        return redirect("/send_temporary_password")
    return render_template("restore_password.html")


@app.route("/send_temporary_password", methods=["GET", "POST"])
def send_temporary_password():
    if request.method == "POST":
        input_valid = input_validation([request.form.get("email"), "Unknown"])
        if input_valid != []:
            flash(input_valid, "info")
            return render_template("send_temporary_password.html")
        session["recovery_email"] = request.form.get("email") 
        temp_password = generate_temporary_password(request.form.get("email"))
        session["temporary_password_hash"] = temp_password[0]
        message = compose_recovery_mail_msg(temp_password[1])
        send_gmail(message, request.form.get("email"))
        temp_password = None
        return redirect("/restore_password")
    return render_template("send_temporary_password.html")


@login_required
@app.route("/track", methods=["POST"])
def track():
    #regex removes <'" ()> from request.form.get("location") value
    filter = """['" ()]"""
    if request.method == "POST" and check_session(request.form.get("location")) == None:
        search_result = Quick_search.query_quick_search()
        print()
        session.pop("track", None)
        session.pop("track_name", None)
        location_name = re.sub(filter,"",request.form.get("location")).split(",")[0]
        location_id = re.sub(filter,"",request.form.get("location")).split(",")[1]
        print(location_name, location_id)
        session["track"] = location_id
        session["track_name"] = location_name
        DATA = get_weather(location_name)
        if set_up_track(session["user_id"], location_id) and type(DATA) != RuntimeError:
            send_gmail(compose_weather_mail_msg(DATA), session["email"])
        return render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass, search_result=search_result) 
    return redirect("/")


@login_required
@app.route("/stop_track", methods=["POST"])
def stop_track():
    if request.method == "POST":
        search_result = Quick_search.query_quick_search()
        session.pop("track", None)
        session.pop("track_name", None)
        if stop_tracking(session["user_id"]):
            location_name = request.form.get("location")
            DATA = get_weather(location_name)
            print("test")
            print(search_result)
            print("test1")
            return redirect("/") if type(DATA) == RuntimeError else render_template("index.html", data=DATA, day_of_week = day_of_week, compass=compass, search_result=search_result) 
    return redirect("/")


class Quick_search():
    """Manages quick search info, saves into buffer, queries info on call, deletes"""

    def write_quick_search_buffer(search_result):
        if session.get("user_id") in temp_storage:
            for i in temp_storage:
                print(i)
                if session.get("user_id") in i:
                    i.update({session.get("user_id") : search_result})
                    return temp_storage
        if session.get("user_id") not in temp_storage:
            temp_storage.append({session.get("user_id") : search_result})
            print(temp_storage)
        return temp_storage
    
    def clear_buffer():
        if session.get("user_id") in temp_storage:
            temp_storage.pop(session.get("user_id"))
            return True
        return False

    def create_quick_search(location, location_list):
        if location_list[0]["search_0"] != location and location_list[1]["search_1"] != location and location_list[2]["search_2"] != location:
            if location_list[0]["search_0"] == None:
                location_list[0].update({"search_0" : location})
            elif location_list[0]["search_0"] != None and location_list[1]["search_1"] == None:
                location_list[1].update({"search_1" : location_list[0]["search_0"]})
                location_list[0] = ({"search_0" : location})
            else:
                location_list[2].update({"search_2":location_list[1]["search_1"]})
                location_list[1].update({"search_1":location_list[0]["search_0"]})
                location_list[0] = ({"search_0" : location})
        return location_list
    
    def query_quick_search():
        if session.get("user_id") != None and session.get("user_id") in temp_storage:
            for i in temp_storage:
                if i.get(session["user_id"]):
                    return {session["user_id"]:i}
            return {"Unknown": location_list}
        return {"Unknown": location_list}


# Checks if track request is already exists
def check_session(location):
    filter = """['" ()]"""
    try:
        if session.get("track") == re.sub(filter,"",location).split(",")[1]:
            return True
        return None
    except: return None


def compass(direction):
    direction = int(direction)
    if direction > 135:
        direction = (direction - 135)
    elif direction < 135:
        direction = (135 - direction)
    return str(direction)
    
        
if __name__=="__main__":
    app.run()    